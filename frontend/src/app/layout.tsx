import './globals.css'

export const metadata = {
  title: 'TraceAtlas',
  description: 'Data Provenance and Lineage Management',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900">{children}</body>
    </html>
  )
}