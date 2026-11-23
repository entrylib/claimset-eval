# Can greybox::alm with a scale model stand in for random effects? Type I error of the averaged
# claimset effect, by simulation. Design: 8 models (4 providers x fast/reasoning), 75 questions,
# 2 conditions; score 0, 1/2, 1 (two binomial points). The effect varies by provider (SD 0.4),
# model (0.3) and question (0.7).
# Two nulls: "population" (the effects are drawn with mean 0: other models and questions are the
# target) and "sample" (the drawn effects are centred so that their mean over these 8 models and
# these 75 questions is exactly 0: these models and questions are the target).
# Model: alm, normal, score ~ condition x type + provider + question (fixed), scale ~ condition + model.
suppressMessages({library(greybox); library(parallel); library(jsonlite)})
args <- commandArgs(TRUE); reps <- if (length(args)) as.integer(args[1]) else 300

one <- function(s, null) {
  set.seed(s)
  mods <- data.frame(model = factor(1:8), provider = factor(rep(1:4, each = 2)), type = rep(0:1, 4))
  qs <- data.frame(question = factor(1:75))
  d <- merge(merge(mods, qs), data.frame(x = 0:1))
  sm_ <- rnorm(4, 0, 0.4)[as.integer(mods$provider)] + rnorm(8, 0, 0.3); sq <- rnorm(75, 0, 0.7)
  if (null == "sample") { sm_ <- sm_ - mean(sm_); sq <- sq - mean(sq) }
  eta <- 0.5 + 0.6 * d$type + rnorm(8, 0, 0.3)[d$model] + rnorm(75, 0, 1.2)[d$question] + d$x * (sm_[d$model] + sq[d$question])
  d$Y <- rbinom(nrow(d), 2, plogis(eta)) / 2
  f <- tryCatch(suppressWarnings(alm(Y ~ x * type + provider + question, d, distribution = "dnorm", scale = ~ x + model)),
                error = function(e) NULL)
  if (is.null(f)) return(NA)
  b <- coef(f); V <- vcov(f); nm <- intersect(names(b), rownames(V)); b <- b[nm]; V <- V[nm, nm]
  L <- setNames(rep(0, length(nm)), nm); L["x"] <- 1; L["x:type"] <- 1/2
  sum(L * b) / sqrt(drop(t(L) %*% V %*% L))
}
out <- list()
for (null in c("population", "sample")) {
  z <- unlist(mclapply(1:reps, one, null = null, mc.cores = 4))
  for (alpha in c(0.05/3, 0.01)) out[[length(out) + 1]] <- list(variable = "rejection rate under no effect, one-sided",
    value = mean(z > qnorm(1 - alpha), na.rm = TRUE),
    conditions = list(null = null, model = "alm, normal, scale ~ condition + model", test = "Wald z",
                      `nominal alpha` = round(alpha, 4), replications = reps))
  out[[length(out) + 1]] <- list(variable = "share of failed fits", value = mean(is.na(z)), conditions = list(null = null, replications = reps))
}
for (x in out) cat(sprintf("%.4f  %s | %s\n", x$value, x$variable, paste(unlist(x$conditions), collapse = " | ")))
p <- Sys.getenv("CLAIMSET_RESULTS"); if (nzchar(p)) write_json(out, p, auto_unbox = TRUE, digits = NA)
