import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Bug Bounty Program Manager',
  description: 'Manage your bug bounty programs with ease',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <main className="min-h-screen bg-figma-bg">
          <div className="figma-container mx-auto p-6">
            {children}
          </div>
        </main>
      </body>
    </html>
  )
}