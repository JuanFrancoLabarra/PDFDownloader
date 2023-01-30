from PDFDownloader import PDFDownloader
import os

PDF = PDFDownloader(f"{os.getcwd()}\\Entradas.csv")
PDF.main()
