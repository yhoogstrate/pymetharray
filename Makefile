
.PHONY: clean all


all: cache/GSM6379997_203927450093_R01C01_Red.idat cache/GSM6379997_203927450093_R01C01_Grn.idat cache/GSM6379998_203927450107_R07C01_Grn.idat.gz cache/GSM6379998_203927450107_R07C01_Red.idat.gz cache/C3L-00365-01_Grn.idat cache/C3L-00365-01_Red.idat

# cache/TCGA-06-0875-01A_Grn.idat cache/TCGA-06-0875-01A_Red.idat



clean:
	rm -rf cache/ ; mkdir -p cache


cache/GSM6379997_203927450093_R01C01_Red.idat:
	mkdir -p cache ;
	wget https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM6379nnn/GSM6379997/suppl/GSM6379997%5F203927450093%5FR01C01%5FRed.idat.gz --output-document=cache/GSM6379997_203927450093_R01C01_Red.idat.gz ;
	gunzip cache/GSM6379997_203927450093_R01C01_Red.idat.gz

cache/GSM6379997_203927450093_R01C01_Grn.idat:
	mkdir -p cache ;
	wget https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM6379nnn/GSM6379997/suppl/GSM6379997%5F203927450093%5FR01C01%5FGrn.idat.gz --output-document=cache/GSM6379997_203927450093_R01C01_Grn.idat.gz ;
	gunzip cache/GSM6379997_203927450093_R01C01_Grn.idat.gz

cache/GSM6379998_203927450107_R07C01_Grn.idat.gz:
	mkdir -p cache ;
	wget https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM6379nnn/GSM6379998/suppl/GSM6379998_203927450107_R07C01_Grn.idat.gz --output-document=cache/GSM6379998_203927450107_R07C01_Grn.idat.gz

cache/GSM6379998_203927450107_R07C01_Red.idat.gz:
	mkdir -p cache ;
	wget https://ftp.ncbi.nlm.nih.gov/geo/samples/GSM6379nnn/GSM6379998/suppl/GSM6379998_203927450107_R07C01_Red.idat.gz --output-document=cache/GSM6379998_203927450107_R07C01_Red.idat.gz

cache/TCGA-06-0875-01A_Grn.idat:
	mkdir -p cache ;
	wget -O cache/TCGA-06-0875-01A_Grn.idat https://api.gdc.cancer.gov/data/0f325cb3-8982-4ca8-bc6f-696b46015637

cache/TCGA-06-0875-01A_Red.idat:
	mkdir -p cache ;
	wget -O cache/TCGA-06-0875-01A_Red.idat https://api.gdc.cancer.gov/data/3d34a4bf-b43c-4fe1-8177-c5de26880ce1



cache/C3L-00365-01_Grn.idat:
	mkdir -p cache ;
	wget -O cache/C3L-00365-01_Grn.idat https://api.gdc.cancer.gov/data/b84e633f-7519-42fb-928f-8ca0ee21a632

cache/C3L-00365-01_Red.idat:
	mkdir -p cache ;
	wget -O cache/C3L-00365-01_Red.idat https://api.gdc.cancer.gov/data/c2307d7b-2a94-48b6-9458-a157e41324e0
