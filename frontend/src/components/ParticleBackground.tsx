import React, { useCallback, useEffect, useState } from "react";
import Particles from "@tsparticles/react";
import { initParticlesEngine } from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import type { Engine } from "@tsparticles/engine";

export default function ParticleBackground() {
  const [init, setInit] = useState(false);

  useEffect(() => {
    initParticlesEngine(async (engine: Engine) => {
      await loadSlim(engine);
    }).then(() => setInit(true));
  }, []);

  const particlesLoaded = useCallback(async () => {}, []);

  if (!init) return null;

  return (
    <Particles
      id="tsparticles"
      particlesLoaded={particlesLoaded}
      className="fixed inset-0 pointer-events-none z-0"
      options={{
        background: { color: { value: "transparent" } },
        fpsLimit: 60,
        interactivity: {
          events: {
            onHover: { enable: true, mode: "repulse" },
            onClick: { enable: true, mode: "push" },
          },
          modes: {
            repulse: { distance: 100, duration: 0.4 },
            push: { quantity: 3 },
          },
        },
        particles: {
          color: { value: ["#a78bfa", "#8b5cf6", "#7c3aed", "#c4b5fd", "#ddd6fe"] },
          links: {
            color: "#8b5cf6",
            distance: 150,
            enable: true,
            opacity: 0.4,
            width: 1.5,
          },
          move: {
            direction: "none",
            enable: true,
            outModes: { default: "bounce" },
            random: true,
            speed: 1.2,
            straight: false,
          },
          number: { 
            density: { 
              enable: true
            }, 
            value: 80 
          },
          opacity: { value: { min: 0.3, max: 0.7 } },
          shape: { type: "circle" },
          size: { value: { min: 2, max: 4 } },
        },
        detectRetina: true,
      }}
    />
  );
}
