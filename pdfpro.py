#!/usr/bin/env python
#
# pdfpro.py
#
# Improve scanned images in pdf files
#

import sys, getopt, io, os.path
import fitz
import PIL.Image

class PdfProcessor:
    def __init__(self):
        self.outputFilename = None

    def processArguments(self, arguments):
        self.initializeArguments(arguments)
        
    def initializeArguments(self, arguments):
        try:
            options, arguments = getopt.getopt(arguments,'ho:')
        except getopt.GetoptError as exception:
            self.error(exception)
        for key, value in options:
            if key == '-h':
                self.usage()
            elif key == '-o':
                if self.outputFilename is None:
                    self.outputFilename = value
                else:
                    self.warn('Multiple output filenames specified')
            else:
                self.error('Unexpected option', key)
        if len(arguments) == 0:
            self.error('Missing arguments')
        if len(arguments) != 1:
            self.error('Only one argument expected')
        self.processFilename(arguments[0])

    def usage(self):
        print('Usage: pdfpro [-h] [-o output_file] FILE')
        print('Improve scanned images in pdf files')
        print('Example: pdfpro my_file.pdf')
        print('  -o  output pdf file')
        print('  -h  help')
        exit(1)
        
    def warn(self, *arguments):
        print(*arguments)
        
    def error(self, *arguments):
        self.warn('pdfpro: ', *arguments)
        self.warn('Try "pdfpro -h" for more information.')
        exit(1)

    def processFilename(self, filename):
        print('Process', filename)
        self.pdf_file = fitz.open(filename)
        numberOfPages = len(self.pdf_file)
        print('Number of pages', numberOfPages)
        new_images = []
        for index in range(numberOfPages):
            print('Process page', index+1, 'of', numberOfPages)
            images = self.pdf_file.get_page_images(index)
            for image in images:
                xref = image[0]
                base_image = self.pdf_file.extract_image(xref)
                image_bytes = base_image['image']
                #image_ext = base_image['ext']
                pil_image = PIL.Image.open(io.BytesIO(image_bytes))
                new_image = self.processImage(pil_image)
                new_images.append(new_image)
        
        basename, extension = os.path.splitext(filename)
        newFilename = basename + '_bw' + extension
        print('Write PDF file', newFilename)
        new_images[0].save(newFilename, save_all=True, append_images=new_images)

    def processImage(self, image):
        image = image.convert('L')
        image = image.point(lambda pixel: 0 if pixel < 160 else 255)
        image = image.convert('1')
        return image

try:
    PdfProcessor().processArguments(sys.argv[1:])
except KeyboardInterrupt:
    print('Interrupted.')
    