from app.evaluation.evaluator import Evaluator


def _format_percent(value: float) -> str:
    return f"{value * 100:.0f}%"


if __name__ == "__main__":
    evaluator = Evaluator()
    report = evaluator.run()
    summary = report["summary"]

    print("\n===============================")
    print("Evaluation Summary")
    print("===============================")
    print()
    print(f"Run ID: {report['run_id']}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Route Accuracy:        {_format_percent(summary['route_accuracy'])}")
    print(f"Answer Accuracy:       {_format_percent(summary['answer_accuracy'])}")
    print(f"Risk Accuracy:         {_format_percent(summary['risk_accuracy'])}")
    print(f"Escalation Accuracy:   {_format_percent(summary['escalation_accuracy'])}")
    print(f"High-Risk Escalation:  {_format_percent(summary['high_risk_escalation_accuracy'])}")
    print(f"Average Latency:       {summary['average_latency']:.2f} sec")
    print(f"P95 Latency:           {summary['p95_latency']:.2f} sec")
    print(f"Overall Score:         {_format_percent(summary['overall_score'])}")
    print()
    print("SLO Status:")
    label_map = {
        "route_accuracy": "Route Accuracy",
        "answer_accuracy": "Answer Accuracy",
        "risk_accuracy": "Risk Accuracy",
        "escalation_accuracy": "High-Risk Escalation",
        "average_latency": "Average Latency",
        "p95_latency": "P95 Latency",
    }
    for metric, passed in summary["slo_status"].items():
        status = "PASS" if passed else "FAIL"
        print(f"  {label_map.get(metric, metric)}: {status}")
    print()
    print("Failed Cases:")
    print("-----------------------")

    if report["failed_cases"]:
        for failure in report["failed_cases"]:
            print(f"Query: {failure['query']}")
            print(
                "Expected: "
                f"route={failure['expected_route']}, "
                f"risk={failure['expected_risk']}, "
                f"escalate={failure['expected_escalate']}, "
                f"answer_contains={failure['expected_answer_contains']}"
            )
            print(
                "Predicted: "
                f"route={failure['predicted_route']}, "
                f"risk={failure['predicted_risk']}, "
                f"escalate={failure['predicted_escalate']}, "
                f"answer={failure['predicted_answer']}"
            )
            print(f"Reason: {failure['reason']}")
            print()
    else:
        print("None")
