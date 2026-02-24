/**
 * Compresse l'image capturée (caméra) ou uploadée en WebP avant de l'envoyer à FastAPI.
 * Permet de réduire drastiquement la bande passante (jusqu'à -80%).
 */
export async function compressToWebP(imageFile, quality = 0.85) {
  return new Promise((resolve) => {
    const canvas = document.createElement('canvas')
    const img = new Image()
    const url = URL.createObjectURL(imageFile)

    img.onload = () => {
      // Résolution maximale pour l'OCR, Gemini lit très bien le 2K.
      const maxSize = 2000
      let { width, height } = img

      if (width > maxSize || height > maxSize) {
        const ratio = Math.min(maxSize / width, maxSize / height)
        width = Math.round(width * ratio)
        height = Math.round(height * ratio)
      }

      canvas.width = width
      canvas.height = height

      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, width, height)

      canvas.toBlob(
        (blob) => {
          URL.revokeObjectURL(url)
          resolve(new File([blob], 'facture.webp', { type: 'image/webp' }))
        },
        'image/webp',
        quality
      )
    }

    img.src = url
  })
}
