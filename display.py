import math

import gobject
import gtk
import cairo

BORDER = 1

def darken_color(c, f=.1):
    f = 1.0 - f
    return gtk.gdk.Color(int(c.red * f), int(c.green * f), int(c.blue * f))

def lighten_color(c, f=.1):
    f = 1.0 + f
    return gtk.gdk.Color(int(c.red * f), int(c.green * f), int(c.blue * f))

def desaturate(c):
    r = int(c.red)
    g = int(c.green)
    b = int(c.blue)

    m = int((r + g + b) / 3.0)
    return gtk.gdk.Color(m, m, m)

def rounded_rectangle(cr, x, y, w, h, r=20):

    if r >= h / 2.0:
        r = h / 2.0

    cr.arc(x + r, y + r, r, math.pi, -.5 * math.pi)
    cr.arc(x + w - r, y + r, r, -.5 * math.pi, 0 * math.pi)
    cr.arc(x + w - r, y + h - r, r, 0 * math.pi, .5 * math.pi)
    cr.arc(x + r, y + h - r, r, .5 * math.pi, math.pi)
    cr.close_path()


class Display(gtk.Widget):

    __gtype_name__ = 'Display'

    def __init__(self):

        gtk.Widget.__init__(self)

        self.title = ''
        self.position = 0.0

        #self.icons = {
        #    'artist': gtk.gdk.pixbuf_new_from_file_at_size('data/icons/artist-mono.svg', 12, 12),
        #    'album': gtk.gdk.pixbuf_new_from_file_at_size('data/icons/album-mono.svg', 12, 12)
        #    }


    def set_title(self, title):

        self.title = title
        self.draw()


    def set_position(self, position):

        self.position = position
        self.draw()


    def do_realize(self):

        self.set_flags(self.flags() | gtk.REALIZED | gtk.NO_WINDOW)
        self.window = self.get_parent_window()
        self.style.attach(self.window)

        style = self.get_style()
        background = style.dark[gtk.STATE_NORMAL]
        self.color = style.dark[gtk.STATE_NORMAL]


    def do_size_request(self, requisition):

        width, height = 32, 32
        requisition.width = width
        requisition.height = height


    def do_size_allocate(self, allocation):
        self.allocation = allocation


    def do_expose_event(self, event):
        self._draw()


    def draw(self):

        if self.window:
            self.window.invalidate_rect(self.allocation, True)


    def _draw(self):

        style = self.get_style()
        background = darken_color(style.bg[gtk.STATE_NORMAL], .05)
        foreground = lighten_color(style.fg[gtk.STATE_NORMAL], .4)
        border = darken_color(background, .3)

        shadow_1 = darken_color(background, 0.15)
        shadow_2 = lighten_color(shadow_1, 0.08)

        width = self.allocation.width
        height = self.allocation.height

        ctx = self.window.cairo_create()
        ctx.set_operator(cairo.OPERATOR_OVER)

        ctx.translate(self.allocation.x, self.allocation.y)
        ctx.set_line_width(1)

        # Draw the shadow...
        ctx.save()
        rounded_rectangle(ctx, BORDER, BORDER, width - 2 * BORDER, height - 2 * BORDER, 5)
        ctx.clip()

        ctx.set_source_rgba(shadow_1.red / 65535.0, shadow_1.green / 65535.0, shadow_1.blue / 65535.0, 1)
        rounded_rectangle(ctx, BORDER, BORDER, width - 2 * BORDER, height - 2 * BORDER, 5)
        ctx.fill()

        ctx.set_source_rgba(shadow_2.red / 65535.0, shadow_2.green / 65535.0, shadow_2.blue / 65535.0, 1)
        rounded_rectangle(ctx, BORDER + 1, BORDER + 1, width - 2 * (BORDER) + 1, height - 2 * (BORDER) + 1, 5)
        ctx.fill()
        ctx.restore()

        # Draw the background...
        ctx.save()
        rounded_rectangle(ctx, BORDER, BORDER, width - 2 * BORDER, height - 2 * BORDER, 5)
        ctx.clip()

        top = lighten_color(background, .04)
        bottom = darken_color(background, .04)
        gradient = cairo.LinearGradient(0, 0, 0, height)
        gradient.add_color_stop_rgba(0, top.red / 65535.0, top.green / 65535.0, top.blue / 65535.0, 1)
        gradient.add_color_stop_rgba(1, bottom.red / 65535.0, bottom.green / 65535.0, bottom.blue / 65535.0, 1)
        ctx.set_source(gradient)

        rounded_rectangle(ctx, BORDER + 2, BORDER + 2, width - 2 * (BORDER) + 2, height - 2 * (BORDER) + 2, 5)
        ctx.fill()
        ctx.restore()

        # Draw frame...
        ctx.save()
        
        top = lighten_color(border, .2)
        bottom = lighten_color(border, .1)
        gradient = cairo.LinearGradient(0, 0, 0, height)
        gradient.add_color_stop_rgba(0, top.red / 65535.0, top.green / 65535.0, top.blue / 65535.0, 1)
        gradient.add_color_stop_rgba(1, bottom.red / 65535.0, bottom.green / 65535.0, bottom.blue / 65535.0, 1)
        ctx.set_source(gradient)
        rounded_rectangle(ctx, BORDER - 1.5, BORDER - 1.5, width - 2 * BORDER + 2, height - 2 * BORDER + 2, 5)
        ctx.clip()
        rounded_rectangle(ctx, BORDER + .5, BORDER + .5, width - 2 * BORDER - 1, height - 2 * BORDER -1, 5)
        ctx.stroke()
        ctx.restore()

        # Draw the position bar's shadow...
        ctx.save()
        rounded_rectangle(ctx, 19, height - 13, width - 38, 7, 20)
        ctx.clip()
        ctx.set_source_rgba(shadow_1.red / 65535.0, shadow_1.green / 65535.0, shadow_1.blue / 65535.0, 1)
        rounded_rectangle(ctx, 20, height - 12, width - 40, 6, 20)
        ctx.clip_preserve()
        ctx.fill()

        ctx.set_source_rgba(shadow_2.red / 65535.0, shadow_2.green / 65535.0, shadow_2.blue / 65535.0, 1)
        rounded_rectangle(ctx, 21.5, height - 11.5, width - 40, 6, 20)
        ctx.fill()
        ctx.restore()

        # Draw the position bar's background...
        ctx.save()
        rounded_rectangle(ctx, 19, height - 13, width - 38, 7, 20)
        ctx.clip()
        ctx.set_source_rgba(background.red / 65535.0, background.green / 65535.0, background.blue / 65535.0, 1)
        rounded_rectangle(ctx, 22.5, height - 10.5, width - 40, 6, 20)
        ctx.fill()
        ctx.restore()

        # Draw the position bar's frame...
        ctx.save()
        ctx.set_source_rgba(border.red / 65535.0, border.green / 65535.0, border.blue / 65535.0, 1)
        rounded_rectangle(ctx, 20.5, height - 12.5, width - 40, 6, 20)
        ctx.stroke()
        ctx.restore()

        ctx.save()
        ctx.set_source_rgba(border.red / 65535.0, border.green / 65535.0, border.blue / 65535.0, 1)        
        rounded_rectangle(ctx, 22, height - 11, self.position * (width - 43), 3)
        ctx.fill()
        ctx.restore()

        ctx.save()
        ctx.set_source_rgba(foreground.red / 65535.0, foreground.green / 65535.0, foreground.blue / 65535.0, 1)
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(11)
        text_x_bearing, text_y_bearing, text_width, text_height = ctx.text_extents(self.title)[:4]
        ctx.move_to((width - text_width) / 2.0, (19 - text_height) / 2 + text_height)
        ctx.show_text(self.title)
        ctx.restore()


if __name__ == '__main__':
    win = gtk.Window()
    t = Display()
    win.add(t)
    win.show_all()
    gtk.main()
