import { createContext, type Dispatch, type ReactNode, type SetStateAction } from 'react'

export const TopbarFilterContext = createContext<
  [ReactNode, Dispatch<SetStateAction<ReactNode>>]
>([null, () => {}])
