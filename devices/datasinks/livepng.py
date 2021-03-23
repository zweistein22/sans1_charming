

from nicos.devices.datasinks.livepng import *

class  PNGLiveFileSinkHandlerF(PNGLiveFileSinkHandler):
      def _writeData(self, data):
        image = np.asarray(data)
        max_pixel = image.max()
        if self.sink.log10:
            zeros = (image == 0)
            image = np.log10(image)
            max_pixel_log = np.log10(max_pixel) if max_pixel else 1
            norm_arr = image.astype(float) * 255. / max_pixel_log
            norm_arr[zeros] = 0
        else:
            if max_pixel == 0:
                norm_arr = image
            else:
                norm_arr = image.astype(float) * 255. / max_pixel
        try:
            if self.sink.rgb:
                norm_arr = norm_arr.astype(np.uint8)
                rgb_arr = np.zeros(image.shape + (3,), np.uint8)
                rgb_arr[..., 0] = LUT_r[norm_arr]
                rgb_arr[..., 1] = LUT_g[norm_arr]
                rgb_arr[..., 2] = LUT_b[norm_arr]
                # Our origin is bottom left, but image origin is top left
                if self.sink.flipy:
                    rgb_arr = np.ascontiguousarray(np.flipud(rgb_arr))
                else:
                    rgb_arr = np.ascontiguousarray(rgb_arr)
                # PIL expects (w, h) but shape is (ny, nx)
                img = Image.frombuffer('RGB', image.shape[::-1], rgb_arr, 'raw',
                        'RGB', 0, 1)
            else:
                hist,bins = np.histogram(norm_arr.flatten(),1024)
                cdf = hist.cumsum()
                cdf_normalized = cdf.astype(float) / cdf.max()
                minval = bins[np.argmax(cdf_normalized>self.sink.histrange[0])]
                maxval = bins[np.argmax(cdf_normalized>self.sink.histrange[1])]
                delta = maxval - minval
                if delta == 0:
                    delta = 1
                img = (norm_arr - minval) / (delta)*255.
                # Our origin is bottom left, but image origin is top left
                if self.sink.flipy:
                    img = np.flipud(img)
                img = np.clip(img, 0 , 255)
                img = Image.fromarray(img.astype(np.uint8))
            img.thumbnail((self.sink.size, self.sink.size),
                      PIL.Image.ANTIALIAS)
            img.save(self.sink.filename)
        except Exception:
            self.log.warning('could not save live PNG', exc=1)
        self._last_saved = currenttime()


class PNGLiveFileSinkF(PNGLiveFileSink):
    parameters = {
        'flipy': Param('Flip image upside down', type=bool,
                          default=True),
    }
    handlerclass = PNGLiveFileSinkHandlerF


