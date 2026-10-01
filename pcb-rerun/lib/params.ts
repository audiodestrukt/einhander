// einhander PCB geometry — kept in lockstep with the enclosure (cad/machine_params.py).
// Switch centers MUST match the deck cutouts so caps line up with the shell.

export const KEY_PITCH = 19.05
export const COLS = 4
export const ROWS = 2
export const KEY_CENTER_X = 3.5 // (MARGIN_L - MARGIN_R)/2  -> matrix shifted toward pinky
export const KEY_CENTER_Y = 7.5 // (MARGIN_B - MARGIN_F)/2  -> matrix pushed forward for a bigger back band

export const keyXY = (col: number, row: number): [number, number] => [
  KEY_CENTER_X + (col - (COLS - 1) / 2) * KEY_PITCH,
  KEY_CENTER_Y + (row - (ROWS - 1) / 2) * KEY_PITCH,
]

// row-major: index = row*COLS + col.  KEY0..3 = back row, KEY4..7 = front row.
export const KEY_XY: [number, number][] = []
for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) KEY_XY.push(keyXY(c, r))

// board fits inside the shell cavity (CAV_X=92.15, CAV_Y=70.05) with ~1mm clearance
export const BOARD_W = 91
export const BOARD_H = 68
export const BACK_Y = -BOARD_H / 2 // back (palm) edge, where USB-C exits (CAD -Y wall)
