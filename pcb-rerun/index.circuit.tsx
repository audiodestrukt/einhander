// einhander — one-handed USB-MIDI controller (RP2040).
// Composes the MCU + power blocks in the back band, with the 8 key switches
// anchored at the enclosure grid, the thumb-cluster header on the left edge,
// a WS2812 status LED, and corner mounting holes.
//
// Cross-block signals share consistent net names (KEY0-7, ENC_*, SHIFT, LED_DIN,
// USB_DP/DM, V3V3, GND) and are reconciled at KiCad export via merge_nets.py.
import { McuBlock } from "./modules/mcu.circuit"
import { PowerBlock } from "./modules/power.circuit"
import { KeySwitch } from "./lib/KeySwitch"
import { WS2812B_B_T } from "./imports/WS2812B_B_T"
import { KEY_XY, BOARD_W, BOARD_H } from "./lib/params"
import { JLCPCB } from "./lib/fab"

export default () => (
  <board width={`${BOARD_W}mm`} height={`${BOARD_H}mm`} layers={4} {...JLCPCB} autorouter="sequential-trace">
    {/* dense clusters in the back (palm-side) band (flat fragments, global nets) */}
    <McuBlock ox={-24} oy={-22} />
    <PowerBlock ox={0} oy={-29} />

    {/* 8 key switches at the enclosure grid */}
    {KEY_XY.map(([x, y], i) => <KeySwitch key={`sw${i}`} name={`SW${i + 1}`} pcbX={x} pcbY={y} />)}
    {KEY_XY.map((_, i) => <trace key={`k${i}`} from={`SW${i + 1}.pin1`} to={`net.KEY${i}`} />)}
    {KEY_XY.map((_, i) => <trace key={`kg${i}`} from={`SW${i + 1}.pin2`} to="net.GND" />)}

    {/* thumb cluster (EC11 + SHIFT live on a left-wall daughterboard) */}
    <pinheader name="J_THUMB" pinCount={5} gender="male" pitch="2.54mm" footprint="pinrow5"
      pinLabels={["ENC_A", "ENC_B", "ENC_SW", "SHIFT", "GND"]}
      pcbX={-40} pcbY={6} pcbRotation={90} showSilkscreenPinLabels />
    <trace from="J_THUMB.ENC_A" to="net.ENC_A" />
    <trace from="J_THUMB.ENC_B" to="net.ENC_B" />
    <trace from="J_THUMB.ENC_SW" to="net.ENC_SW" />
    <trace from="J_THUMB.SHIFT" to="net.SHIFT" />
    <trace from="J_THUMB.GND" to="net.GND" />

    {/* WS2812 cyan "active" indicator */}
    <WS2812B_B_T name="D1" pcbX={-41} pcbY={-6} />
    <trace from="D1.pin1" to="net.V3V3" />
    <trace from="D1.pin3" to="net.GND" />
    <trace from="D1.pin4" to="net.LED_DIN" />
    <capacitor name="C_LED" capacitance="100nF" footprint="0805" pcbX={-41} pcbY={-11} />
    <trace from="C_LED.pin1" to="net.V3V3" />
    <trace from="C_LED.pin2" to="net.GND" />

    {/* boot/reset buttons on the free front edge (accessible, out of the back band) */}
    <pushbutton name="SW_BOOT" footprint="pushbutton" pcbX={36} pcbY={-17} />
    <trace from="SW_BOOT.pin1" to="net.BOOT_BTN" />
    <trace from="SW_BOOT.pin2" to="net.GND" />
    <pushbutton name="SW_RST" footprint="pushbutton" pcbX={36} pcbY={-27} />
    <trace from="SW_RST.pin1" to="net.RUN" />
    <trace from="SW_RST.pin2" to="net.GND" />

    {/* corner mounting holes (M2) */}
    <hole diameter="2.4mm" pcbX={-BOARD_W / 2 + 3} pcbY={-BOARD_H / 2 + 3} />
    <hole diameter="2.4mm" pcbX={BOARD_W / 2 - 3} pcbY={-BOARD_H / 2 + 3} />
    <hole diameter="2.4mm" pcbX={-BOARD_W / 2 + 3} pcbY={BOARD_H / 2 - 3} />
    <hole diameter="2.4mm" pcbX={BOARD_W / 2 - 3} pcbY={BOARD_H / 2 - 3} />
  </board>
)
