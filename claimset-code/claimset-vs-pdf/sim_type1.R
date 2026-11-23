# Type I error of candidate tests of the averaged claimset effect, by simulation under no average effect.
# Design of the plan: 8 models (4 providers x fast/reasoning), questions crossed with models, 2 conditions.
# Data-generating process as in the design review: the claimset effect varies by provider (SD 0.4),
# by model within provider (SD 0.3) and by question (SD 0.7, or 0.3), with mean 0.
# Outcome: binary (the flag models), and a score of 0, 1/2, 1 analysed as 2 binomial points.
suppressMessages({library(lme4); library(blme); library(parallel); library(jsonlite)})
args <- commandArgs(TRUE); reps <- if (length(args)) as.integer(args[1]) else 400

one <- function(s, nq, size, sdq) {
  set.seed(s)
  mods <- data.frame(model = factor(1:8), provider = factor(rep(1:4, each = 2)), type = rep(0:1, 4))
  qs <- data.frame(question = factor(1:nq), paper = factor(rep(1:5, length.out = nq)))
  d <- merge(merge(mods, qs), data.frame(x = 0:1))
  slope_m <- rnorm(4, 0, 0.4)[as.integer(mods$provider)] + rnorm(8, 0, 0.3)
  eta <- 0.5 + 0.6 * d$type + rnorm(8, 0, 0.3)[d$model] + rnorm(nq, 0, 1.2)[d$question] +
         d$x * (slope_m[d$model] + rnorm(nq, 0, sdq)[d$question])
  d$y <- rbinom(nrow(d), size, plogis(eta)); d$n <- size
  fx <- cbind(y, n - y) ~ x * type + paper + provider
  fits <- list(
    glmer  = function() glmer(update(fx, . ~ . + (1 + x | model) + (1 + x | question)), d, family = binomial),
    bglmer = function() bglmer(update(fx, . ~ . + (1 + x | model) + (1 + x | question)), d, family = binomial),
    bglmer_prov = function() bglmer(update(fx, . ~ . + (1 + x | provider) + (1 + x | model) + (1 + x | question)), d, family = binomial))
  out <- sapply(names(fits), function(k) {
    f <- tryCatch(suppressWarnings(suppressMessages(fits[[k]]())), error = function(e) NULL)
    if (is.null(f)) return(c(NA, NA))
    b <- fixef(f); V <- as.matrix(vcov(f)); L <- setNames(rep(0, length(b)), names(b))
    L["x"] <- 1; L["x:type"] <- 1/2
    c(sum(L * b) / sqrt(drop(t(L) %*% V %*% L)), isSingular(f))
  })
  out
}

res <- list()
for (sc in list(list(nq = 25, size = 1, sdq = 0.7), list(nq = 75, size = 2, sdq = 0.7), list(nq = 75, size = 2, sdq = 0.3))) {
  r <- simplify2array(mclapply(1:reps, one, nq = sc$nq, size = sc$size, sdq = sc$sdq, mc.cores = 4))
  cond <- list(questions = sc$nq, outcome = if (sc$size == 1) "binary" else "score as 2 points", `question slope SD` = sc$sdq, replications = reps)
  for (k in dimnames(r)[[2]]) {
    z <- r[1, k, ]; sing <- r[2, k, ]
    tests <- list(c("Wald z", qnorm(0.99), qnorm(1 - 0.01/3)), c("Wald t, 6 df", qt(0.99, 6), qt(1 - 0.01/3, 6)),
                  c("Wald t, 3 df", qt(0.99, 3), qt(1 - 0.01/3, 3)))
    for (tt in tests) for (a in 1:2) {
      crit <- as.numeric(tt[a + 1]); alpha <- c(0.01, 0.01/3)[a]
      res[[length(res) + 1]] <- list(variable = "rejection rate under no effect, one-sided", value = mean(z > crit, na.rm = TRUE),
        conditions = c(cond, list(model = k, test = tt[1], `nominal alpha` = round(alpha, 4))))
    }
    res[[length(res) + 1]] <- list(variable = "share of singular fits", value = mean(sing, na.rm = TRUE), conditions = c(cond, list(model = k)))
    res[[length(res) + 1]] <- list(variable = "share of failed fits", value = mean(is.na(z)), conditions = c(cond, list(model = k)))
  }
}
for (x in res) if (x$variable != "share of failed fits") cat(sprintf("%-45s %s\n", sprintf("%.4f", x$value), paste(unlist(x$conditions), collapse = " | ")))
p <- Sys.getenv("CLAIMSET_RESULTS"); if (nzchar(p)) write_json(res, p, auto_unbox = TRUE, digits = NA)
