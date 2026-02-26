import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, test, vi } from 'vitest'

// ── Mocks ────────────────────────────────────────────────────────────────────

vi.mock('framer-motion', () => ({
  AnimatePresence: ({ children }) => <>{children}</>,
  motion: {
    div: ({
      children, className, onClick, style,
      role, 'aria-modal': ariaModal, 'aria-labelledby': ariaLabelledby,
      ...rest
    }) => (
      <div
        className={className}
        onClick={onClick}
        style={style}
        role={role}
        aria-modal={ariaModal}
        aria-labelledby={ariaLabelledby}
        data-testid="motion-div"
        ref={rest.ref}
      >
        {children}
      </div>
    ),
  },
}))

vi.mock('recharts', () => ({
  AreaChart: () => null,
  Area: () => null,
  XAxis: () => null,
  YAxis: () => null,
  Tooltip: () => null,
  ResponsiveContainer: ({ children }) => <div data-testid="chart-container">{children}</div>,
}))

vi.mock('sonner', () => ({
  toast: { info: vi.fn(), error: vi.fn(), success: vi.fn() },
}))

vi.mock('../services/apiClient', () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: { results: [] } }),
  },
}))

vi.mock('../config/api', () => ({
  ENDPOINTS: {
    compare: 'http://localhost:8000/api/v1/catalogue/compare',
  },
}))

// ── Import after mocks ────────────────────────────────────────────────────────
import CompareModal from '../components/CompareModal'
import apiClient from '../services/apiClient'

// ── Tests ─────────────────────────────────────────────────────────────────────
describe('CompareModal', () => {
  const onClose = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('visibility', () => {
    test('renders nothing when isOpen is false', () => {
      const { container } = render(<CompareModal isOpen={false} onClose={onClose} />)
      expect(container.firstChild).toBeNull()
    })

    test('renders the modal when isOpen is true', () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      expect(screen.getByText('Comparateur Prix')).toBeInTheDocument()
    })

    test('shows the search input placeholder', () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      expect(screen.getByPlaceholderText(/ciment/i)).toBeInTheDocument()
    })
  })

  describe('close button', () => {
    test('calls onClose when X button is clicked', async () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      const buttons = screen.getAllByRole('button')
      const closeBtn = buttons.find((b) => b.querySelector('svg'))
      expect(closeBtn).toBeDefined()
      await userEvent.click(closeBtn)
      expect(onClose).toHaveBeenCalledTimes(1)
    })

    test('calls onClose when backdrop is clicked', async () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      const motionDivs = screen.getAllByTestId('motion-div')
      // The outer backdrop div calls onClose
      fireEvent.click(motionDivs[0])
      expect(onClose).toHaveBeenCalled()
    })
  })

  describe('search input', () => {
    test('updates on user typing', async () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      const input = screen.getByPlaceholderText(/ciment/i)
      await userEvent.type(input, 'ciment')
      expect(input.value).toBe('ciment')
    })

    test('Comparer button is disabled when search is too short', () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      const btn = screen.getByRole('button', { name: /comparer/i })
      expect(btn).toBeDisabled()
    })

    test('Comparer button enabled after typing 2+ chars', async () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      const input = screen.getByPlaceholderText(/ciment/i)
      await userEvent.type(input, 'ci')
      const btn = screen.getByRole('button', { name: /comparer/i })
      expect(btn).not.toBeDisabled()
    })
  })

  describe('initialSearch prop', () => {
    test('pre-fills the search input', () => {
      render(<CompareModal isOpen={true} onClose={onClose} initialSearch="tube cuivre" />)
      const input = screen.getByPlaceholderText(/ciment/i)
      expect(input.value).toBe('tube cuivre')
    })
  })

  describe('empty state', () => {
    test('shows placeholder text when no results', () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      expect(
        screen.getByText(/recherchez un produit pour comparer les prix/i)
      ).toBeInTheDocument()
    })
  })

  describe('API search', () => {
    test('calls apiClient.get on Comparer button click', async () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      const input = screen.getByPlaceholderText(/ciment/i)
      await userEvent.type(input, 'ciment')
      const btn = screen.getByRole('button', { name: /comparer/i })
      await userEvent.click(btn)
      await waitFor(() => {
        expect(apiClient.get).toHaveBeenCalled()
      })
    })

    test('displays results returned from API', async () => {
      apiClient.get.mockResolvedValueOnce({
        data: {
          results: [
            {
              fournisseur: 'BigMat',
              designation_fr: 'Ciment 42.5R sac 35kg',
              prix_remise_ht: '11.25',
              unite: 'sac',
              remise_pct: 10,
              price_history: [],
            },
          ],
        },
      })

      render(<CompareModal isOpen={true} onClose={onClose} initialSearch="ciment" />)
      const btn = screen.getByRole('button', { name: /comparer/i })
      await userEvent.click(btn)

      await waitFor(() => {
        expect(screen.getByText('Ciment 42.5R sac 35kg')).toBeInTheDocument()
      })
      expect(screen.getByText('BigMat')).toBeInTheDocument()
    })
  })

  describe('accessibility', () => {
    test('has role="dialog" and aria-modal="true"', () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-modal', 'true')
    })

    test('dialog is labelled by the title via aria-labelledby', () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      const dialog = screen.getByRole('dialog')
      expect(dialog).toHaveAttribute('aria-labelledby', 'compare-modal-title')
      const title = document.getElementById('compare-modal-title')
      expect(title).toHaveTextContent('Comparateur Prix')
    })

    test('close button has an accessible label', () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      expect(screen.getByRole('button', { name: /fermer/i })).toBeInTheDocument()
    })

    test('Escape key calls onClose', async () => {
      render(<CompareModal isOpen={true} onClose={onClose} />)
      await userEvent.keyboard('{Escape}')
      expect(onClose).toHaveBeenCalledTimes(1)
    })

    test('restores focus to trigger element on close', () => {
      const triggerRef = { current: document.createElement('button') }
      document.body.appendChild(triggerRef.current)
      triggerRef.current.focus()

      const { rerender } = render(
        <CompareModal isOpen={true} onClose={onClose} triggerRef={triggerRef} />
      )
      rerender(
        <CompareModal isOpen={false} onClose={onClose} triggerRef={triggerRef} />
      )

      expect(document.activeElement).toBe(triggerRef.current)
      document.body.removeChild(triggerRef.current)
    })
  })
})
