import cv2
import numpy as np

def draw_shape(canvas, shape_type, size, is_filled=True):
    """
    在画布上绘制简单图形
    shape_type: 'circle'、'square'、'circle_hollow'、'square_hollow'
    size: 图形大小
    is_filled: 是否填充
    """
    center = (size // 2, size // 2)
    if shape_type == 'circle' or shape_type == 'circle_hollow':
        if shape_type == 'circle' or is_filled:
            cv2.circle(canvas, center, size // 3, 255, -1)
        else:
            cv2.circle(canvas, center, size // 3, 255, 2)
    elif shape_type == 'square' or shape_type == 'square_hollow':
        half_size = size // 3
        pt1 = (center[0] - half_size, center[1] - half_size)
        pt2 = (center[0] + half_size, center[1] + half_size)
        if shape_type == 'square' or is_filled:
            cv2.rectangle(canvas, pt1, pt2, 255, -1)
        else:
            cv2.rectangle(canvas, pt1, pt2, 255, 2)
    return canvas

# -----------------------------------------------------------
# --- helper: create a square canvas with centred text ---
# -----------------------------------------------------------
def make_text_canvas(content, size, font_scale, thickness, color, rot):
    """
    Returns a (size×size) single-channel uint8 image with the given content
    centred and rotated by `rot` (0 / 90 / 180 / 270° clockwise).
    content can be text or shape type ('circle'、'square'、'circle_hollow'、'square_hollow')
    """
    canvas = np.zeros((size, size), dtype=np.uint8)

    if content in ['circle', 'square', 'circle_hollow', 'square_hollow']:
        is_filled = not (content.endswith('_hollow'))
        base_type = content.replace('_hollow', '')
        canvas = draw_shape(canvas, content, size, is_filled=is_filled)
    else:
        # --- draw the (possibly multi-line) text centred on the canvas ---
        lines = content.split("\n")
        line_sizes = [cv2.getTextSize(line,
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    font_scale, thickness)[0] for line in lines]
        total_h = sum(h for (_, h) in line_sizes) + (len(lines)-1)*int(line_sizes[0][1]*0.3)
        y = (size - total_h) // 2 + line_sizes[0][1]

        for (w, h), line in zip(line_sizes, lines):
            x = (size - w) // 2
            cv2.putText(canvas, line, (x, y),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        font_scale, 255, thickness, cv2.LINE_AA)
            y += h + int(h*0.3)  # small vertical gap

    # --- rotate the whole canvas (multiples of 90°) ---
    if rot == 90:
        canvas = cv2.rotate(canvas, cv2.ROTATE_90_CLOCKWISE)
    elif rot == 180:
        canvas = cv2.rotate(canvas, cv2.ROTATE_180)
    elif rot == 270:
        canvas = cv2.rotate(canvas, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif rot != 0:
        raise ValueError("Rotation must be 0, 90, 180 or 270 degrees.")

    # recolour to BGR so we can overlay easily later
    coloured = cv2.cvtColor(canvas, cv2.COLOR_GRAY2BGR)
    coloured[canvas > 0] = color            # set glyph pixels to text colour
    return coloured, canvas                 # return both image and mask


# -----------------------------------------------------------
# --- main: draw cube ---------------------------------------
# -----------------------------------------------------------
def draw_cube(up_text="X",
              front_text="A",
              right_text="B",
              up_rot=0, front_rot=0, right_rot=0,   # NEW
              size=200,           # edge length (px) of the cube's front face
              offset_ratio=0.4,   # depth as a fraction of size (0-1)
              bg_color=(255, 255, 255),
              face_color=(255, 255, 255),
              edge_color=(0, 0, 0),
              text_color=(0, 0, 0),
              edge_thick=2,
              font_scale=1.8,
              font_thick=2):
    """
    Returns an image (numpy array, BGR) of a cube whose three visible faces
    carry the supplied texts, each rotated by the given angles.

    Rotations are clockwise in degrees: 0, 90, 180, 270
    """
    depth = int(size * offset_ratio)
    pad = size // 2
    h = size + abs(depth) + pad * 2
    w = size + depth + pad * 2
    img = np.full((h, w, 3), bg_color, dtype=np.uint8)

    # --- cube vertex coordinates -----------------------------------
    p0 = (pad,              pad + abs(depth))
    p1 = (pad + size,       pad + abs(depth))
    p2 = (pad + size,       pad + abs(depth) + size)
    p3 = (pad,              pad + abs(depth) + size)

    dx, dy = depth, -depth
    p4 = (p0[0] + dx, p0[1] + dy)
    p5 = (p1[0] + dx, p1[1] + dy)
    p6 = (p5[0],       p5[1] + size)

    # --- paint faces (back→front so overlapping looks right) --------
    cv2.fillPoly(img, [np.int32([p4, p5, p1, p0])], face_color)  # top
    cv2.fillPoly(img, [np.int32([p1, p5, p6, p2])], face_color)  # right
    cv2.fillPoly(img, [np.int32([p0, p1, p2, p3])], face_color)  # front

    # --- helper: warp a (square) text canvas to a quadrilateral -----
    def warp_to_quad(text, rot, quad):
        canvas, mask = make_text_canvas(text, size,
                                        font_scale, font_thick,
                                        text_color, rot)
        src = np.float32([[0, 0],
                          [size, 0],
                          [size, size],
                          [0, size]])
        dst = np.float32(quad)
        M = cv2.getPerspectiveTransform(src, dst)
        warped   = cv2.warpPerspective(canvas, M, (w, h),
                                       flags=cv2.INTER_LINEAR,
                                       borderMode=cv2.BORDER_TRANSPARENT)
        warped_m = cv2.warpPerspective(mask, M, (w, h),
                                       flags=cv2.INTER_NEAREST,
                                       borderMode=cv2.BORDER_CONSTANT,
                                       borderValue=0)

        # overlay: only copy pixels where mask is white
        img[warped_m > 0] = warped[warped_m > 0]

    # ­­­--- place the three texts -----------------------------------
    warp_to_quad(front_text, front_rot, [p0, p1, p2, p3])  # front face
    warp_to_quad(up_text,    up_rot,    [p4, p5, p1, p0])  # top face
    warp_to_quad(right_text, right_rot, [p1, p5, p6, p2])  # right face

    # --- redraw edges so they sit on top of everything --------------
    edges = [
        (p0, p1), (p1, p2), (p2, p3), (p3, p0),   # front
        (p0, p4), (p1, p5), (p4, p5),             # top
        (p2, p6), (p5, p6)                        # right
    ]
    for a, b in edges:
        cv2.line(img, a, b, edge_color, edge_thick, cv2.LINE_AA)

    return img


# -------------------------------------------------------------------
# --- demo / quick test ---------------------------------------------
# -------------------------------------------------------------------
if __name__ == "__main__":
    cube_img = draw_cube(
        up_text   ="R",
        front_text="P",
        right_text="Q",
        up_rot=180, front_rot=270, right_rot=270,
        size=300, offset_ratio=0.35,
        text_color=(0, 0, 0),
        font_scale=7
    )

    cv2.imwrite("cube.png", cube_img)
    cv2.imshow("Cube", cube_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

