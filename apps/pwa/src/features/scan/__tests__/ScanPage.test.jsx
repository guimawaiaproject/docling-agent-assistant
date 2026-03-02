import React from 'react'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, test, vi } from 'vitest'

vi.mock('framer-motion', () => {
  const React = require('react') // eslint-disable-line no-undef
  const Motion = ({ children, whileTap: _wt, whileHover: _wh, ...props }) =>
    React.createElement('div', props, children)
  return {
    AnimatePresence: ({ children }) => children,
    motion: {
      div: Motion,
      button: Motion,
      span: Motion,
    },
  }
})

vi.mock('react-dropzone', () => ({
  useDropzone: (opts) => ({
    getRootProps: () => ({ 'data-testid': 'dropzone' }),
    getInputProps: () => ({}),
    isDragActive: false,
    acceptedFiles: [],
    fileRejections: [],
    ...opts,
  }),
}))

vi.mock('sonner', () => ({ toast: { error: vi.fn(), success: vi.fn(), info: vi.fn() } }))
vi.mock('@splinetool/react-spline', () => ({
  default: () => React.createElement('div', { 'data-testid': 'spline-scene' }),
}))
vi.mock('@/components/SplineScene', () => ({
  default: () => React.createElement('div', { 'data-testid': 'spline-scene' }),
}))
vi.mock('@/shared/lib/apiClient', () => ({ default: { post: vi.fn(), get: vi.fn() } }))
vi.mock('@/shared/lib/offlineQueue', () => ({
  enqueueUpload: vi.fn(),
  getPendingCount: vi.fn(() => 0),
  getPendingUploads: vi.fn(() => []),
  removePendingUpload: vi.fn(),
}))
vi.mock('@/shared/lib/imageService', () => ({ compressToWebP: vi.fn((f) => Promise.resolve(f)) }))

const mockAddToQueue = vi.fn()
const mockClearQueue = vi.fn()
const mockUpdateItem = vi.fn()
const mockRemoveFromQueue = vi.fn()
const mockSetJobStart = vi.fn()
const mockSetJobComplete = vi.fn()
vi.mock('@/store/useStore', () => ({
  useDoclingStore: (selector) => {
    const state = {
      batchQueue: [],
      addToQueue: mockAddToQueue,
      clearQueue: mockClearQueue,
      updateQueueItem: mockUpdateItem,
      removeFromQueue: mockRemoveFromQueue,
      setJobStart: mockSetJobStart,
      setJobComplete: mockSetJobComplete,
      selectedModel: 'gemini-3-flash-preview',
    }
    return typeof selector === 'function' ? selector(state) : state
  },
}))

import ScanPage from '../ScanPage'

describe('ScanPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('affiche la dropzone au chargement', () => {
    render(
      <MemoryRouter>
        <ScanPage />
      </MemoryRouter>
    )
    expect(screen.getByTestId('scan-dropzone')).toBeInTheDocument()
  })

  test('affiche un texte invitant à déposer des fichiers', () => {
    render(
      <MemoryRouter>
        <ScanPage />
      </MemoryRouter>
    )
    expect(
      screen.getByText(/Glisser-déposer des PDF \/ images/i)
    ).toBeInTheDocument()
  })
})
