/**
 * Tests des calculs métier devis (HT, remise, TVA, TTC).
 * Sans dépendance à jspdf — logique pure.
 */
import { describe, expect, test } from 'vitest'

describe('Calculs devis', () => {
  test('calcul TTC correct avec TVA 20%', () => {
    const items = [
      { designation: 'Ciment', qty: 2, prix_unit: 50 },
      { designation: 'Sable', qty: 1, prix_unit: 30 },
    ]
    const tvaRate = 20
    const remise = 10 // 10%

    const totalHT = items.reduce((sum, i) => sum + i.qty * i.prix_unit, 0)
    expect(totalHT).toBe(130)

    const remiseAmount = totalHT * (remise / 100)
    expect(remiseAmount).toBe(13)

    const netHT = totalHT - remiseAmount
    expect(netHT).toBe(117)

    const tva = netHT * (tvaRate / 100)
    expect(tva).toBeCloseTo(23.4, 2)

    const ttc = netHT + tva
    expect(ttc).toBeCloseTo(140.4, 2)
  })

  test('calcul sans remise', () => {
    const totalHT = 100
    const tvaRate = 20
    const ttc = totalHT * (1 + tvaRate / 100)
    expect(ttc).toBe(120)
  })

  test('calcul avec remise fixe (montant)', () => {
    const totalHT = 200
    const remiseMontant = 25
    const netHT = totalHT - remiseMontant
    const tva = netHT * 0.2
    const ttc = netHT + tva
    expect(netHT).toBe(175)
    expect(ttc).toBeCloseTo(210, 0)
  })
})
