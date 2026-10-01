// Power block: USB-C receptacle (VBUS + USB data + CC pulldowns) -> AP2112K 3.3V LDO.
// FLAT fragment (global net scope), positioned via (ox,oy). USB-C mouth faces the
// back edge (CAD -Y wall) so the cable exits the enclosure.
import { TYPE_C_31_M_12 } from "../imports/TYPE_C_31_M_12"
import { AP2112K_3_3TRG1 } from "../imports/AP2112K_3_3TRG1"
import { JLCPCB } from "../lib/fab"

export const PowerBlock = ({ ox = 0, oy = 0 }: { ox?: number; oy?: number }) => {
  const X = (x: number) => ox + x
  const Y = (y: number) => oy + y
  return (
    <>
      <TYPE_C_31_M_12 name="J1" pcbX={X(0)} pcbY={Y(0)} pcbRotation={0} />
      <AP2112K_3_3TRG1 name="U3" pcbX={X(16)} pcbY={Y(0)} />

      {/* VBUS / GND / shield */}
      <trace from="J1.B4A9" to="net.VBUS" />
      <trace from="J1.A4B9" to="net.VBUS" />
      {["A1B12", "B1A12", "EH1", "EH2", "EH3", "EH4"].map((p) => <trace key={p} from={`J1.${p}`} to="net.GND" />)}

      {/* CC pulldowns -> 5V UFP/device */}
      <resistor name="R_CC1" resistance="5.1k" footprint="0402" layer="bottom" pcbX={X(-1.25)} pcbY={Y(0)} />
      <resistor name="R_CC2" resistance="5.1k" footprint="0402" layer="bottom" pcbX={X(1.75)} pcbY={Y(0)} />
      <trace from="J1.A5" to="R_CC1.pin1" />
      <trace from="R_CC1.pin2" to="net.GND" />
      <trace from="J1.B5" to="R_CC2.pin1" />
      <trace from="R_CC2.pin2" to="net.GND" />

      {/* USB 2.0 data — both A/B sides tied for reversibility */}
      <trace from="J1.A6" to="net.USB_DP" />
      <trace from="J1.B6" to="net.USB_DP" />
      <trace from="J1.A7" to="net.USB_DM" />
      <trace from="J1.B7" to="net.USB_DM" />

      {/* LDO */}
      <trace from="U3.VIN" to="net.VBUS" />
      <trace from="U3.EN" to="net.VBUS" />
      <trace from="U3.GND" to="net.GND" />
      <trace from="U3.VOUT" to="net.V3V3" />
      <capacitor name="C_IN" capacitance="1uF" footprint="0805" pcbX={X(8)} pcbY={Y(0)} />
      <trace from="C_IN.pin1" to="net.VBUS" />
      <trace from="C_IN.pin2" to="net.GND" />
      <capacitor name="C_OUT" capacitance="1uF" footprint="0805" pcbX={X(24)} pcbY={Y(0)} />
      <trace from="C_OUT.pin1" to="net.V3V3" />
      <trace from="C_OUT.pin2" to="net.GND" />
    </>
  )
}

export default () => (
  <board width="34mm" height="22mm" {...JLCPCB}>
    <PowerBlock />
  </board>
)
