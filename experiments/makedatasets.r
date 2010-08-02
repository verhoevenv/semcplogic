#run with "R CMD BATCH --vanilla makedatasets.r"

library(sem)

data(Klein)
Klein$P.lag <- c(NA, Klein$P[-22])
Klein$X.lag <- c(NA, Klein$X[-22])
Klein$A <- Klein$Year - 1931
Klein <- Klein[-1,]
Klein$Year <- NULL
Klein$G <- NULL
Klein$T <- NULL
colnames(Klein) <- c("c","p","wp","i","klag","x","wg","plag","xlag","a")
dataset <- Klein
write.csv(dataset,row.names=FALSE,file="kleindata.csv")

data(CNES)
colnames(CNES) <- c("mbsa2","mbsa7","mbsa8","mbsa9")
dataset <- CNES
write.csv(dataset,row.names=FALSE,file="cnesdata.csv")
