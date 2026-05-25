#!/usr/bin/env python3
"""Semantic regression checks for commercial-legal contract routing."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = (ROOT / "commercial-legal" / "skills" / "review" / "SKILL.md").read_text(encoding="utf-8")
SERVICE = (ROOT / "commercial-legal" / "skills" / "service-engagement-review" / "SKILL.md").read_text(encoding="utf-8")
PUBLIC = (ROOT / "commercial-legal" / "skills" / "public-sector-contract-overlay" / "SKILL.md").read_text(encoding="utf-8")
REFERENCE = (ROOT / "commercial-legal" / "references" / "public-sector-contract-core.md").read_text(encoding="utf-8")


SCENARIO_MARKERS = {
    "ordinary consulting service": ("咨询服务", "一般服务与委托合同审查层"),
    "property appraisal engagement": ("评估委托", "一般服务与委托合同审查层"),
    "government purchased service": ("政府购买服务", "公共部门合同审查层"),
    "administrative compensation signal": ("安置", "行政协议属性"),
    "nda specialist route": ("保密协议", "保密协议审查"),
    "saas specialist route": ("SaaS", "SaaS审查"),
}


def main() -> int:
    failures: list[str] = []
    for scenario, markers in SCENARIO_MARKERS.items():
        for marker in markers:
            if marker not in REVIEW:
                failures.append(f"{scenario}: missing routing marker {marker}")
    for marker in ("成果与标准", "时间与里程碑", "费用与支付", "验收与异议"):
        if marker not in SERVICE:
            failures.append(f"service review missing control {marker}")
    for marker in ("主体与权限", "预算与采购/购买服务", "行政协议属性", "强制上报"):
        if marker not in PUBLIC:
            failures.append(f"public-sector overlay missing control {marker}")
    for marker in ("财政部令第102号", "最高人民法院关于审理行政协议案件若干问题的规定", "地方规则保留"):
        if marker not in REFERENCE:
            failures.append(f"public-sector reference missing source/boundary {marker}")
    if failures:
        print("Commercial routing regression failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Commercial routing regression OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
