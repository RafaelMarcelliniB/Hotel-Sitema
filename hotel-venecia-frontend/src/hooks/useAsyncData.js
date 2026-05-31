import { useEffect, useState } from 'react'

export function useAsyncData(fetcher, dependencies = []) {
  const [data, setData] = useState(undefined)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let mounted = true

    const load = async () => {
      try {
        setIsLoading(true)
        const result = await fetcher()
        if (mounted) {
          setData(result)
          setError(null)
        }
      } catch (err) {
        if (mounted) {
          setError(err)
        }
      } finally {
        if (mounted) {
          setIsLoading(false)
        }
      }
    }

    load()

    return () => {
      mounted = false
    }
  }, dependencies)

  return { data, isLoading, error }
}
