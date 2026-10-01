import type { ChipProps } from "@tscircuit/props"

const pinLabels = {
  pin1: ["pin1"],
  pin2: ["pin2"]
} as const

export const MX1A_11NW = (props: ChipProps<typeof pinLabels>) => {
  return (
    <chip
      pinLabels={pinLabels}
      supplierPartNumbers={{
  "jlcpcb": [
    "C3316924"
  ]
}}
      manufacturerPartNumber="MX1A_11NW"
      footprint={<footprint>
        <hole pcbX="5.08mm" pcbY="-3.0649989mm" diameter="1.7018mm" />
<hole pcbX="-5.08mm" pcbY="-3.0649989mm" diameter="1.7018mm" />
<hole pcbX="0mm" pcbY="-3.0649989mm" diameter="3.999992mm" />
<platedhole  portHints={["pin2"]} pcbX="2.54mm" pcbY="2.0150011mm" outerDiameter="2.1999956mm" holeDiameter="1.5000224mm" shape="circle" />
<platedhole  portHints={["pin1"]} pcbX="-3.81mm" pcbY="-0.5249989mm" outerDiameter="2.1999956mm" holeDiameter="1.5000224mm" shape="circle" />
<silkscreentext text="{NAME}" pcbX="-0.0127mm" pcbY="5.7328011mm" anchorAlignment="center" fontSize="1mm" />
<courtyardoutline outline={[{"x":-8.073200000000043,"y":4.982801100000074},{"x":8.047800000000052,"y":4.982801100000074},{"x":8.047800000000052,"y":-11.138198899999907},{"x":-8.073200000000043,"y":-11.138198899999907},{"x":-8.073200000000043,"y":4.982801100000074}]} />
      </footprint>}
      cadModel={{
        objUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C3316924.obj?uuid=82a0b1b0736d4246abdfab1c08b9c459",
        stepUrl: "https://modelcdn.tscircuit.com/easyeda_models/assets/C3316924.step?uuid=82a0b1b0736d4246abdfab1c08b9c459",
        pcbRotationOffset: 0,
        modelOriginPosition: { x: 0.015011399999934838, y: 3.079984899999772, z: 0.09999359999999946 },
      }}
      {...props}
    />
  )
}