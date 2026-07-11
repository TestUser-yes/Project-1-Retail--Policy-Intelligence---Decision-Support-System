// Data export utilities

export interface ExportOptions {
  format: "csv" | "json";
  filename?: string;
  includeHeaders?: boolean;
}

export const exportData = {
  // Export metrics to CSV
  toCSV: (data: any[], headers: string[], options: Partial<ExportOptions> = {}): void => {
    const { filename = "data.csv" } = options;

    // Create CSV content
    const csvContent = [
      headers.join(","),
      ...data.map((row) =>
        headers.map((header) => {
          const value = row[header];
          return typeof value === "string" ? `"${value}"` : value;
        }).join(",")
      ),
    ].join("\n");

    // Create and download file
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
  },

  // Export metrics to JSON
  toJSON: (data: any, options: Partial<ExportOptions> = {}): void => {
    const { filename = "data.json" } = options;

    const jsonContent = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonContent], { type: "application/json" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
  },

  // Export metrics report as text
  toText: (data: string, filename: string = "report.txt"): void => {
    const blob = new Blob([data], { type: "text/plain" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(url);
  },

  // Generate metrics report
  generateReport: (metrics: any[]): string => {
    const timestamp = new Date().toLocaleString();
    const lines = [
      "METRICS REPORT",
      "==============",
      "",
      `Generated: ${timestamp}`,
      `Total Records: ${metrics.length}`,
      "",
      "Summary:",
      metrics
        .map(
          (m) =>
            `- SLO Compliance: ${(m.slo_compliance_rate * 100).toFixed(1)}% | ` +
            `Avg Latency: ${m.average_latency_ms.toFixed(0)}ms | ` +
            `Success Rate: ${(m.success_rate * 100).toFixed(1)}%`
        )
        .join("\n"),
    ];

    return lines.join("\n");
  },
};
