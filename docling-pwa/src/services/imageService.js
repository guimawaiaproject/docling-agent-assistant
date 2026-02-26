const MAX_SIZE = 2000

/**
 * Compresse une image en WebP. Reduit la bande passante ~80%.
 */
export function compressToWebP(imageFile, quality = 0.85) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    const url = URL.createObjectURL(imageFile)

    img.onload = () => {
      try {
        let { width, height } = img
        if (width > MAX_SIZE || height > MAX_SIZE) {
          const ratio = Math.min(MAX_SIZE / width, MAX_SIZE / height)
          width  = Math.round(width * ratio)
          height = Math.round(height * ratio)
        }

        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height

        const ctx = canvas.getContext('2d', { alpha: false })
        ctx.drawImage(img, 0, 0, width, height)

        canvas.toBlob(
          (blob) => {
            URL.revokeObjectURL(url)
            if (!blob) { reject(new Error('Compression failed')); return }
            resolve(new File([blob], imageFile.name.replace(/\.\w+$/, '.webp'), { type: 'image/webp' }))
          },
          'image/webp',
          quality,
        )
      } catch (e) {
        URL.revokeObjectURL(url)
        reject(e)
      }
    }

    img.onerror = () => {
      URL.revokeObjectURL(url)
      reject(new Error(`Cannot read ${imageFile.name}`))
    }

    img.src = url
  })
}