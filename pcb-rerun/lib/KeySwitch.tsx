// Cherry MX (PCB-mount) keyswitch. No JLC part — hand-soldered — so we model the
// footprint directly: 2 plated contacts + the 4mm center post + 2 alignment holes.
// Electrically just a 2-terminal SPST (pin1 -> GPIO, pin2 -> GND).
import type { CommonLayoutProps } from "@tscircuit/props"

interface Props extends CommonLayoutProps {
  name: string
}

export const KeySwitch = ({ name, ...props }: Props) => (
  <chip
    name={name}
    pinLabels={{ pin1: "A", pin2: "B" }}
    footprint={
      <footprint>
        {/* electrical contacts (Cherry MX standard offsets) */}
        <platedhole portHints={["pin1"]} pcbX="-3.81mm" pcbY="2.54mm" shape="circle" holeDiameter="1.5mm" outerDiameter="2.5mm" />
        <platedhole portHints={["pin2"]} pcbX="2.54mm" pcbY="5.08mm" shape="circle" holeDiameter="1.5mm" outerDiameter="2.5mm" />
        {/* mechanical: center pole + 2 alignment pins */}
        <hole diameter="4mm" pcbX="0mm" pcbY="0mm" />
        <hole diameter="1.7mm" pcbX="-5.08mm" pcbY="0mm" />
        <hole diameter="1.7mm" pcbX="5.08mm" pcbY="0mm" />
        {/* 14mm body outline */}
        <silkscreenpath route={[
          { x: -7, y: -7 }, { x: 7, y: -7 }, { x: 7, y: 7 }, { x: -7, y: 7 }, { x: -7, y: -7 },
        ]} />
      </footprint>
    }
    // Cherry MX 3D model (EasyEDA C3316924) — visual only; our footprint's origin is at
    // the switch center, so no Y shift is needed (the imported part offsets Y by ~3mm
    // because its footprint origin sits above the switch center).
    cadModel={{
      objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C3316924.obj?uuid=82a0b1b0736d4246abdfab1c08b9c459",
      stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C3316924.step?uuid=82a0b1b0736d4246abdfab1c08b9c459",
      pcbRotationOffset: 0,
      modelOriginPosition: { x: 0, y: 0, z: 0 },
    }}
    {...props}
  />
)
