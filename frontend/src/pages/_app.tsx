import "@/styles/globals.css";
import type { AppProps } from "next/app";
import dynamic from "next/dynamic";
import Layout from "@/components/Layout";
import { ToastProvider } from "@/components/Notifications";

// Load particles client-side only (no SSR)
const ParticleBackground = dynamic(
  () => import("@/components/ParticleBackground"),
  { ssr: false }
);

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <ParticleBackground />
      <ToastProvider />
      <Layout>
        <Component {...pageProps} />
      </Layout>
    </>
  );
}
