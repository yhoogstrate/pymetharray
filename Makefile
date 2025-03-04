
.PHONY: clean all


all: cache/GSM6379997_203927450093_R01C01_Red.idat cache/GSM6379997_203927450093_R01C01_Grn.idat cache/GSM6379998_203927450107_R07C01_Grn.idat.gz cache/GSM6379998_203927450107_R07C01_Red.idat.gz



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


