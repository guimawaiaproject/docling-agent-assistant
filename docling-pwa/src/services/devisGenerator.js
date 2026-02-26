/**
 * DevisGenerator - Generate BTP quote PDFs from selected catalogue products.
 * Uses jspdf + jspdf-autotable for PDF generation client-side.
 */

const DEVIS_STORAGE_KEY = 'docling_devis_counter'

function getNextCounter() {
  const year = new Date().getFullYear()
  const stored = localStorage.getItem(DEVIS_STORAGE_KEY)
  let counter = 1
  if (stored) {
    const [storedYear, storedCounter] = stored.split('-').map(Number)
    counter = storedYear === year ? storedCounter + 1 : 1
  }
  localStorage.setItem(DEVIS_STORAGE_KEY, `${year}-${counter}`)
  return `DEV-${year}-${String(counter).padStart(3, '0')}`
}

export function getNextDevisNum() {
  return getNextCounter()
}

export function getPreviewDevisNum() {
  const year = new Date().getFullYear()
  const stored = localStorage.getItem(DEVIS_STORAGE_KEY)
  let counter = 1
  if (stored) {
    const [storedYear, storedCounter] = stored.split('-').map(Number)
    counter = storedYear === year ? storedCounter + 1 : 1
  }
  return `DEV-${year}-${String(counter).padStart(3, '0')}`
}

import jsPDF from 'jspdf'
import 'jspdf-autotable'

export function generateDevisPDF(products, options = {}) {
  const {
    entreprise = 'Mon Entreprise BTP',
    client = 'Client',
    devisNum = `DEV-${new Date().getFullYear()}-001`,
    tvaRate = 21,
    remiseGlobale = 0,
    remiseType = 'percent',
  } = options

  const doc = new jsPDF('p', 'mm', 'a4')
  const pageW = doc.internal.pageSize.getWidth()
  let y = 15

  // Header
  doc.setFontSize(20)
  doc.setFont('helvetica', 'bold')
  doc.text(entreprise, 14, y)
  y += 8

  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text(`Devis N: ${devisNum}`, 14, y)
  doc.text(`Date: ${new Date().toLocaleDateString('fr-FR')}`, pageW - 14, y, { align: 'right' })
  y += 6
  doc.text(`Client: ${client}`, 14, y)
  y += 10

  // Line separator
  doc.setDrawColor(200)
  doc.line(14, y, pageW - 14, y)
  y += 5

  // Table
  const rows = products.map((p, i) => [
    i + 1,
    p.designation_fr || p.designation_raw || '',
    p.unite || 'u',
    p.quantite || 1,
    (parseFloat(p.prix_remise_ht) || 0).toFixed(2),
    ((parseFloat(p.prix_remise_ht) || 0) * (p.quantite || 1)).toFixed(2),
  ])

  doc.autoTable({
    startY: y,
    head: [['#', 'Designation', 'Unite', 'Qte', 'PU HT', 'Total HT']],
    body: rows,
    theme: 'grid',
    headStyles: {
      fillColor: [15, 23, 42],
      textColor: [255, 255, 255],
      fontStyle: 'bold',
      fontSize: 9,
    },
    bodyStyles: { fontSize: 8 },
    columnStyles: {
      0: { cellWidth: 10, halign: 'center' },
      1: { cellWidth: 'auto' },
      2: { cellWidth: 18, halign: 'center' },
      3: { cellWidth: 15, halign: 'center' },
      4: { cellWidth: 25, halign: 'right' },
      5: { cellWidth: 28, halign: 'right' },
    },
    margin: { left: 14, right: 14 },
  })

  y = doc.lastAutoTable.finalY + 10

  // Totals
  let totalHT = products.reduce((acc, p) =>
    acc + (parseFloat(p.prix_remise_ht) || 0) * (p.quantite || 1), 0
  )
  const remiseAmount = remiseType === 'percent'
    ? totalHT * (remiseGlobale / 100)
    : Math.min(remiseGlobale, totalHT)
  const totalHTAfterRemise = totalHT - remiseAmount
  const tva = totalHTAfterRemise * (tvaRate / 100)
  const totalTTC = totalHTAfterRemise + tva

  const rightX = pageW - 14
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text(`Total HT:`, rightX - 45, y)
  doc.text(`${totalHT.toFixed(2)} EUR`, rightX, y, { align: 'right' })
  y += 6
  if (remiseAmount > 0) {
    doc.text(`Remise ${remiseType === 'percent' ? remiseGlobale + '%' : ''}:`, rightX - 45, y)
    doc.text(`-${remiseAmount.toFixed(2)} EUR`, rightX, y, { align: 'right' })
    y += 6
    doc.text(`Total HT apres remise:`, rightX - 45, y)
    doc.text(`${totalHTAfterRemise.toFixed(2)} EUR`, rightX, y, { align: 'right' })
    y += 6
  }
  doc.text(`TVA ${tvaRate}%:`, rightX - 45, y)
  doc.text(`${tva.toFixed(2)} EUR`, rightX, y, { align: 'right' })
  y += 6
  doc.setFont('helvetica', 'bold')
  doc.setFontSize(12)
  doc.text(`Total TTC:`, rightX - 45, y)
  doc.text(`${totalTTC.toFixed(2)} EUR`, rightX, y, { align: 'right' })

  // Footer
  y += 15
  doc.setFontSize(8)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(150)
  doc.text('Devis genere par Docling Agent BTP', 14, y)

  doc.save(`${devisNum}.pdf`)
  return devisNum
}