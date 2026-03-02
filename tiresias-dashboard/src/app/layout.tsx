import type { Metadata } from 'next';
import './globals.css';
import { SkipLinks } from '@/components/accessibility/SkipLinks';
import { LiveRegion } from '@/components/accessibility/LiveRegion';
import { Header } from '@/components/common/Header';
import { Footer } from '@/components/common/Footer';

export const metadata: Metadata = {
  title: 'Tiresias - AI Audio Description for Videos',
  description:
    'Accurate, timely audio descriptions for the blind and visually impaired community',
  keywords: 'accessibility, audio description, blind, visually impaired, video',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <meta charSet="utf-8" />
        <meta name="theme-color" content="#141414" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, maximum-scale=5"
        />
      </head>
      <body className="font-sans bg-background text-foreground">
        <LiveRegion>
          <SkipLinks />

          <div className="min-h-screen flex flex-col">
            <Header />

            <main
              id="main-content"
              role="main"
              className="flex-1 container mx-auto px-4 py-8"
              tabIndex={-1}
            >
              {children}
            </main>

            <Footer />
          </div>
        </LiveRegion>
      </body>
    </html>
  );
}
