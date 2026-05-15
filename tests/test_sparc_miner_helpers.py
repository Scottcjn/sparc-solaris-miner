import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "rustchain_sparc_miner.py"
SPEC = importlib.util.spec_from_file_location("rustchain_sparc_miner", MODULE_PATH)
miner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(miner)


def test_check_vm_detection_reports_all_virtualization_warnings():
    warnings = miner.check_vm_detection(
        {
            "is_zone": True,
            "is_ldom": True,
            "hostid": "00000000",
        }
    )

    assert "Running in Solaris Zone - minimal rewards" in warnings
    assert "Running in LDOM - minimal rewards" in warnings
    assert "Invalid hostid - may be VM" in warnings


def test_get_sparc_cpu_info_parses_ultrasparc_iie(monkeypatch):
    def fake_check_output(cmd, stderr=None):
        if cmd == ["/usr/sbin/prtconf", "-v"]:
            return b"cpu, instance #0\n    compatible: 'SUNW,UltraSPARC-IIe'\n"
        if cmd == ["/usr/sbin/psrinfo", "-v"]:
            return (
                b"Status of virtual processor 0 as of: online\n"
                b"  The sparcv9 processor operates at 500 MHz,\n"
                b"  and has an UltraSPARC-IIe implementation.\n"
                b"Status of virtual processor 1 as of: online\n"
            )
        raise AssertionError("unexpected command: %r" % (cmd,))

    monkeypatch.setattr(miner.subprocess, "check_output", fake_check_output)

    cpu_info = miner.get_sparc_cpu_info()

    assert cpu_info["model"] == "UltraSPARC-IIe"
    assert cpu_info["family"] == "UltraSPARC-IIe"
    assert cpu_info["clock_mhz"] == 500
    assert cpu_info["ncpus"] == 2
    assert cpu_info["impl"] == "UltraSPARC-IIe"


def test_get_sparc_cpu_info_falls_back_to_sparc_t_family(monkeypatch):
    def fake_check_output(cmd, stderr=None):
        if cmd == ["/usr/sbin/prtconf", "-v"]:
            return b"cpu, instance #0\n    name='SUNW,UltraSPARC-T1'\n"
        if cmd == ["/usr/sbin/psrinfo", "-v"]:
            return b"Status of virtual processor 0 as of: online\n  operates at 1200 MHz\n"
        raise AssertionError("unexpected command: %r" % (cmd,))

    monkeypatch.setattr(miner.subprocess, "check_output", fake_check_output)

    cpu_info = miner.get_sparc_cpu_info()

    assert cpu_info["model"] == "UltraSPARC-T1"
    assert cpu_info["family"] == "SPARC-T"
    assert cpu_info["clock_mhz"] == 1200
    assert cpu_info["ncpus"] == 1


def test_make_request_serializes_json_and_routes_https_through_proxy(monkeypatch):
    captured = {}

    class FakeResponse:
        def read(self):
            return b'{"ok": true, "source": "fake"}'

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["data"] = request.data
        captured["timeout"] = timeout
        captured["user_agent"] = request.get_header("User-agent")
        captured["content_type"] = request.get_header("Content-type")
        return FakeResponse()

    monkeypatch.setattr(miner, "urlopen", fake_urlopen)

    result = miner.make_request(
        "https://node.example/attest/submit",
        data={"miner": "wallet", "nonce": 7},
        method="POST",
        proxy="http://proxy.local:8888",
    )

    assert result == {"ok": True, "source": "fake"}
    assert captured["url"] == "http://proxy.local:8888/https://node.example/attest/submit"
    assert json.loads(captured["data"].decode("utf-8")) == {"miner": "wallet", "nonce": 7}
    assert captured["timeout"] == 30
    assert captured["user_agent"] == "RustChain-SPARC-Miner/%s" % miner.VERSION
    assert captured["content_type"] == "application/json"


def test_submit_attestation_builds_stable_payload(monkeypatch):
    captured = {}

    def fake_make_request(url, data=None, method="GET", proxy=None):
        captured["url"] = url
        captured["data"] = data
        captured["method"] = method
        captured["proxy"] = proxy
        return {"ok": True}

    monkeypatch.setattr(miner, "make_request", fake_make_request)
    monkeypatch.setattr(miner, "get_solaris_version", lambda: "Solaris 10 8/11 s10s_u10wos_17b")
    monkeypatch.setattr(miner.time, "time", lambda: 1234.567)

    result = miner.submit_attestation(
        "wallet-1",
        {
            "model": "UltraSPARC-IIe",
            "family": "UltraSPARC-IIe",
            "clock_mhz": 500,
            "ncpus": 2,
        },
        {
            "hostid": "80ff12ab",
            "prtconf_hash": "abc123",
            "obp_version": "OBP 4.17",
            "memory_mb": 1024,
            "is_zone": False,
            "is_ldom": False,
        },
        "https://node.example",
        proxy="http://proxy.local:8888",
    )

    assert result == {"ok": True}
    assert captured["url"] == "https://node.example/attest/submit"
    assert captured["method"] == "POST"
    assert captured["proxy"] == "http://proxy.local:8888"
    assert captured["data"]["miner"] == "wallet-1"
    assert captured["data"]["miner_id"] == "wallet-1-80ff12ab"
    assert captured["data"]["nonce"] == 1234567
    assert captured["data"]["device"] == {
        "model": "UltraSPARC-IIe",
        "arch": "sparc",
        "family": "UltraSPARC-IIe",
        "device_arch": "ultrasparc_iie",
        "clock_mhz": 500,
        "ncpus": 2,
    }
    assert captured["data"]["report"]["os_version"] == "Solaris 10 8/11 s10s_u10wos_17b"
    assert captured["data"]["fingerprint"]["all_passed"] is True
