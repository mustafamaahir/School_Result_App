import jsPDF from "jspdf";
import "jspdf-autotable";

export const generateResultsPDF = (
  studentName,
  results,
  selectedTerm,
  selectedSession,
  termPositions,
  academicAnalysis
) => {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  let yPos = 20;

  // Header
  doc.setFillColor(11, 61, 46); // Islamic green
  doc.rect(0, 0, pageWidth, 35, "F");
  doc.setTextColor(255, 255, 255);
  doc.setFontSize(16);
  doc.setFont(undefined, "bold");
  doc.text("DAARUL-FAOZ FOR ARABIC & ISLAMIC STUDIES", pageWidth / 2, 15, {
    align: "center",
  });
  doc.setFontSize(12);
  doc.text("Academic Results Report", pageWidth / 2, 25, { align: "center" });

  yPos = 45;

  // Student Info
  doc.setTextColor(0, 0, 0);
  doc.setFontSize(11);
  doc.setFont(undefined, "bold");
  doc.text(`Student Name: ${studentName}`, 14, yPos);
  yPos += 7;
  doc.setFont(undefined, "normal");
  doc.text(`Session: ${selectedSession}`, 14, yPos);
  yPos += 7;
  doc.text(`Term: ${selectedTerm}`, 14, yPos);
  yPos += 10;

  // Performance Summary
  if (selectedTerm !== "All" && termPositions[selectedTerm]) {
    const termData = termPositions[selectedTerm];
    const filteredResults = results.filter(
      (r) =>
        (selectedTerm === "All" || r.term === selectedTerm) &&
        (selectedSession === "All" || r.session === selectedSession)
    );

    const avgScore =
      filteredResults.length > 0
        ? (
            filteredResults.reduce((acc, r) => acc + Number(r.percentage), 0) /
            filteredResults.length
          ).toFixed(2)
        : 0;
    const highestScore = Math.max(...filteredResults.map((r) => r.percentage));
    const lowestScore = Math.min(...filteredResults.map((r) => r.percentage));

    doc.setFillColor(240, 248, 255);
    doc.rect(14, yPos, pageWidth - 28, 35, "F");
    doc.setFont(undefined, "bold");
    doc.setFontSize(12);
    doc.text("Performance Summary", 18, yPos + 7);

    doc.setFont(undefined, "normal");
    doc.setFontSize(10);
    yPos += 15;
    doc.text(`Average Score: ${avgScore}%`, 18, yPos);
    doc.text(`Highest Score: ${highestScore}%`, 80, yPos);
    yPos += 6;
    doc.text(`Lowest Score: ${lowestScore}%`, 18, yPos);
    doc.text(
      `Subjects: ${termData.subjects_taken} / ${termData.total_subjects}`,
      80,
      yPos
    );
    yPos += 6;
    if (termData.position_label) {
      doc.setFont(undefined, "bold");
      doc.text(
        `Position in Class: ${termData.position_label}`,
        18,
        yPos
      );
    }
    yPos += 15;
  }

  // Results Table
  doc.setFont(undefined, "bold");
  doc.setFontSize(12);
  doc.text("Detailed Results", 14, yPos);
  yPos += 5;

  const tableData = results
    .filter(
      (r) =>
        (selectedTerm === "All" || r.term === selectedTerm) &&
        (selectedSession === "All" || r.session === selectedSession)
    )
    .map((r) => [
      r.session,
      r.term,
      r.student_class,
      r.subject,
      `${r.percentage}%`,
      r.min_score_in_class,
      r.max_score_in_class,
      r.median_score_in_class,
    ]);

  doc.autoTable({
    startY: yPos,
    head: [
      [
        "Session",
        "Term",
        "Class",
        "Subject",
        "Score",
        "Min",
        "Max",
        "Median",
      ],
    ],
    body: tableData,
    theme: "grid",
    headStyles: {
      fillColor: [11, 61, 46],
      textColor: [255, 255, 255],
      fontSize: 9,
      fontStyle: "bold",
    },
    bodyStyles: { fontSize: 8 },
    columnStyles: {
      4: { halign: "center", fontStyle: "bold" },
      5: { halign: "center" },
      6: { halign: "center" },
      7: { halign: "center" },
    },
    margin: { left: 14, right: 14 },
  });

  yPos = doc.lastAutoTable.finalY + 10;

  // Academic Analysis
  if (academicAnalysis) {
    // Check if new page needed
    if (yPos > 240) {
      doc.addPage();
      yPos = 20;
    }

    doc.setFillColor(102, 126, 234);
    doc.rect(14, yPos, pageWidth - 28, 8, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFont(undefined, "bold");
    doc.setFontSize(11);
    doc.text("Academic Performance Analysis", 18, yPos + 5.5);

    yPos += 12;
    doc.setTextColor(0, 0, 0);
    doc.setFont(undefined, "normal");
    doc.setFontSize(9);

    const splitText = doc.splitTextToSize(academicAnalysis, pageWidth - 32);
    splitText.forEach((line) => {
      if (yPos > 280) {
        doc.addPage();
        yPos = 20;
      }
      doc.text(line, 16, yPos);
      yPos += 5;
    });
  }

  // Footer
  const pageCount = doc.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(128, 128, 128);
    doc.text(
      `Generated on ${new Date().toLocaleDateString()}`,
      14,
      doc.internal.pageSize.getHeight() - 10
    );
    doc.text(
      `Page ${i} of ${pageCount}`,
      pageWidth - 30,
      doc.internal.pageSize.getHeight() - 10
    );
  }

  // Save PDF
  const fileName = `${studentName.replace(/\s+/g, "_")}_Results_${selectedTerm.replace(/\s+/g, "_")}.pdf`;
  doc.save(fileName);
};