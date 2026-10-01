// MCU block: RP2040 + QSPI flash + 12MHz crystal + decoupling + BOOTSEL series-R.
// FLAT fragment (global net scope) positioned via (ox,oy) so the freeroute DSN has
// one unified net per signal (no per-subcircuit fragmentation). U1 rotated 270° so
// QSPI/USB/power face +X (flash + USB-C to the right), XIN/XOUT face -X (crystal),
// GPIO18-29 face +Y toward the switches. Small passives + decoupling on BOTTOM.
// BOOTSEL/RESET buttons live at the top level (front edge) — see index.
import { RP2040 } from "../imports/RP2040"
import { W25Q16JVSSIQ } from "../imports/W25Q16JVSSIQ"
import { X322512MSB4SI } from "../imports/X322512MSB4SI"
import { JLCPCB } from "../lib/fab"

const V3V3_PINS = ["IOVDD1", "IOVDD2", "IOVDD3", "IOVDD4", "IOVDD5", "IOVDD6", "USB_VDD", "ADC_AVDD", "VREG_IN"]
const DECAP_POS: [number, number][] = [
  [-6, 7], [-3, 7], [0, 7], [3, 7], [6, 7], [-6, -7], [-3, -7],  // clear of under-QFN B.Cu escape
]

export const McuBlock = ({ ox = 0, oy = 0 }: { ox?: number; oy?: number }) => {
  const X = (x: number) => ox + x
  const Y = (y: number) => oy + y
  return (
    <>
      <RP2040 name="U1" pcbX={X(0)} pcbY={Y(0)} pcbRotation={270} />
      <W25Q16JVSSIQ name="U2" pcbX={X(12)} pcbY={Y(0)} />
      <X322512MSB4SI name="Y1" pcbX={X(-12)} pcbY={Y(0)} />

      {/* power */}
      {V3V3_PINS.map((p) => <trace key={p} from={`U1.${p}`} to="net.V3V3" />)}
      <trace from="U1.VREG_VOUT" to="net.DVDD" />
      <trace from="U1.DVDD1" to="net.DVDD" />
      <trace from="U1.DVDD2" to="net.DVDD" />
      <trace from="U1.GND" to="net.GND" />
      <trace from="U1.TESTEN" to="net.GND" />

      {/* QSPI flash */}
      <trace from="U1.QSPI_SS" to="net.QSPI_SS" />
      <trace from="U1.QSPI_SCLK" to="net.QSPI_SCLK" />
      <trace from="U1.QSPI_SD0" to="net.QSPI_SD0" />
      <trace from="U1.QSPI_SD1" to="net.QSPI_SD1" />
      <trace from="U1.QSPI_SD2" to="net.QSPI_SD2" />
      <trace from="U1.QSPI_SD3" to="net.QSPI_SD3" />
      <trace from="U2.pin1" to="net.QSPI_SS" />{/* /CS */}
      <trace from="U2.CLK" to="net.QSPI_SCLK" />
      <trace from="U2.pin5" to="net.QSPI_SD0" />{/* DI/IO0 */}
      <trace from="U2.pin2" to="net.QSPI_SD1" />{/* DO/IO1 */}
      <trace from="U2.IO2" to="net.QSPI_SD2" />
      <trace from="U2.IO3" to="net.QSPI_SD3" />
      <trace from="U2.VCC" to="net.V3V3" />
      <trace from="U2.GND" to="net.GND" />
      <capacitor name="C15" capacitance="100nF" footprint="0402" layer="bottom" pcbX={X(12)} pcbY={Y(-4)} />
      <trace from="C15.pin1" to="net.V3V3" />
      <trace from="C15.pin2" to="net.GND" />

      {/* crystal + load caps */}
      <trace from="U1.XIN" to="net.XIN" />
      <trace from="U1.XOUT" to="net.XOUT" />
      <trace from="Y1.OSC1" to="net.XIN" />
      <trace from="Y1.OSC2" to="net.XOUT" />
      <trace from="Y1.GND1" to="net.GND" />
      <trace from="Y1.GND2" to="net.GND" />
      <capacitor name="C12" capacitance="15pF" footprint="0402" layer="bottom" pcbX={X(-12)} pcbY={Y(3)} />
      <trace from="C12.pin1" to="net.XIN" />
      <trace from="C12.pin2" to="net.GND" />
      <capacitor name="C13" capacitance="15pF" footprint="0402" layer="bottom" pcbX={X(-12)} pcbY={Y(-3)} />
      <trace from="C13.pin1" to="net.XOUT" />
      <trace from="C13.pin2" to="net.GND" />

      {/* USB */}
      <trace from="U1.USB_DM" to="net.USB_DM" />
      <trace from="U1.USB_DP" to="net.USB_DP" />

      {/* GPIO: 8 keys, encoder, shift, LED (assignment is firmware-flexible) */}
      {Array.from({ length: 8 }).map((_, i) => <trace key={`k${i}`} from={`U1.GPIO${i}`} to={`net.KEY${i}`} />)}
      <trace from="U1.GPIO8" to="net.ENC_A" />
      <trace from="U1.GPIO9" to="net.ENC_B" />
      <trace from="U1.GPIO10" to="net.ENC_SW" />
      <trace from="U1.GPIO11" to="net.SHIFT" />
      <trace from="U1.GPIO16" to="net.LED_DIN" />

      {/* RUN pull-up + filter (RESET button is top-level) */}
      <trace from="U1.RUN" to="net.RUN" />
      <resistor name="R_RUN" resistance="10k" footprint="0402" layer="bottom" pcbX={X(-9)} pcbY={Y(4)} />
      <trace from="R_RUN.pin1" to="net.V3V3" />
      <trace from="R_RUN.pin2" to="net.RUN" />
      <capacitor name="C14" capacitance="100nF" footprint="0402" layer="bottom" pcbX={X(-9)} pcbY={Y(-4)} />
      <trace from="C14.pin1" to="net.RUN" />
      <trace from="C14.pin2" to="net.GND" />

      {/* BOOTSEL series R (button top-level): QSPI_SS -> 1k -> BOOT_BTN */}
      <resistor name="R_BOOT" resistance="1k" footprint="0402" layer="bottom" pcbX={X(9)} pcbY={Y(-4)} />
      <trace from="R_BOOT.pin1" to="net.QSPI_SS" />
      <trace from="R_BOOT.pin2" to="net.BOOT_BTN" />

      {/* decoupling (bottom): 7x100nF V3V3 under QFN, DVDD 1uF+100nF, 10uF bulk */}
      {DECAP_POS.map(([x, y], i) => (
        <capacitor key={`d${i}`} name={`C${i + 1}`} capacitance="100nF" footprint="0402"
          layer="bottom" pcbX={X(x)} pcbY={Y(y)} decouplingFor="U1" decouplingTo="net.GND" />
      ))}
      {DECAP_POS.map((_, i) => <trace key={`dv${i}`} from={`C${i + 1}.pin1`} to="net.V3V3" />)}
      {DECAP_POS.map((_, i) => <trace key={`dg${i}`} from={`C${i + 1}.pin2`} to="net.GND" />)}
      <capacitor name="C9" capacitance="1uF" footprint="0402" layer="bottom" pcbX={X(0)} pcbY={Y(-7)} />
      <trace from="C9.pin1" to="net.DVDD" />
      <trace from="C9.pin2" to="net.GND" />
      <capacitor name="C10" capacitance="100nF" footprint="0402" layer="bottom" pcbX={X(3)} pcbY={Y(-7)} />
      <trace from="C10.pin1" to="net.DVDD" />
      <trace from="C10.pin2" to="net.GND" />
      <capacitor name="C11" capacitance="10uF" footprint="0805" layer="bottom" pcbX={X(6.5)} pcbY={Y(-7)} />
      <trace from="C11.pin1" to="net.V3V3" />
      <trace from="C11.pin2" to="net.GND" />
    </>
  )
}

export default () => (
  <board width="46mm" height="34mm" {...JLCPCB}>
    <McuBlock />
  </board>
)
