import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, test, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

// ── Mocks ────────────────────────────────────────────────────────────────────

vi.mock('@tanstack/react-virtual', () => ({
  useVirtualizer: () => ({
    getVirtualItems: () => [],
    getTotalSize: () => 0,
    measureElement: () => {},
  }),
}))

vi.mock('exceljs', () => ({
  default: {
    Workbook: vi.fn(() => ({
      addWorksheet: vi.fn(() => ({
        columns: [],
        addRows: vi.fn(),
      })),
      xlsx: { writeBuffer: vi.fn().mockResolvedValue(new ArrayBuffer(0)) },
    })),
  },
}))

vi.mock('sonner', () => ({
  toast: { error: vi.fn(), success: vi.fn() },
}))

const mockGet = vi.fn()
vi.mock('../services/apiClient', () => ({
  default: { get: (...args) => mockGet(...args) },
}))

vi.mock('../config/api', () => ({
  ENDPOINTS: {
    catalogue: '/api/v1/catalogue',
    fournisseurs: '/api/v1/catalogue/fournisseurs',
  },
}))

// ── Import after mocks ────────────────────────────────────────────────────────
import CataloguePage from '../CataloguePage'

function renderWithRouter() {
  return render(
    <MemoryRouter initialEntries={['/catalogue']}>
      <Routes>
        <Route path="/catalogue" element={<CataloguePage />} />
        <Route path="/scan" element={<div data-testid="scan-page">Scan Page</div>} />
      </Routes>
    </MemoryRouter>
  )
}

// ── Tests ─────────────────────────────────────────────────────────────────────
describe('CataloguePage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGet.mockImplementation((url) => {
      if (url === '/api/v1/catalogue' || url?.includes?.('catalogue')) {
        return Promise.resolve({ data: { products: [], total: 0, has_more: false } })
      }
      if (url === '/api/v1/catalogue/fournisseurs' || url?.includes?.('fournisseurs')) {
        return Promise.resolve({ data: { fournisseurs: [] } })
      }
      return Promise.resolve({ data: {} })
    })
  })

  test('mock API returns 0 products, CTA "Scanner une facture" is present', async () => {
    renderWithRouter()

    await waitFor(() => {
      expect(mockGet).toHaveBeenCalled()
    })

    expect(screen.getByText('Scanner une facture')).toBeInTheDocument()
    expect(screen.getByTestId('cta-scan-facture')).toBeInTheDocument()
  })

  test('clicking CTA navigates to /scan', async () => {
    const { container } = renderWithRouter()

    await waitFor(() => {
      expect(screen.getByTestId('cta-scan-facture')).toBeInTheDocument()
    })

    const cta = screen.getByTestId('cta-scan-facture')
    await userEvent.click(cta)

    await waitFor(() => {
      expect(screen.getByTestId('scan-page')).toBeInTheDocument()
    })
  })
})
