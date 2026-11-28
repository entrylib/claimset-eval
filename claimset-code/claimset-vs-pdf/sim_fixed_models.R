# Models fixed, questions random: level and power of the test of the claimset effect averaged over the
# models. Design: 2 x P models (P providers x fast/reasoning; P = 4 by default, 3 after DeepSeek was dropped), 2 conditions; flags on 25 questions,
# score (two binomial points) on 75. The effect varies by provider (SD 0.4), model (0.3) and question (0.7).
# Null: the effect averaged over these models is 0 (model effects centred in the sample); question
# effects are drawn with mean 0 (other questions are part of the target).
# Model: glmer, logit, y ~ condition x model + (1 + condition | question); the tested quantity is the
# mean of the model effects, by Wald z and by t on (questions - 1) degrees of freedom.
suppressMessages({library(lme4); library(parallel); library(jsonlite)})
args <- commandArgs(TRUE); reps0 <- if (length(args) > 0) as.integer(args[1]) else 1000
reps1 <- if (length(args) > 1) as.integer(args[2]) else 300
P <- if (length(args) > 2) as.integer(args[3]) else 4; M <- 2 * P

one <- function(s, nq, size, delta) {
  set.seed(s)
  mods <- data.frame(model = factor(1:M), provider = factor(rep(1:P, each = 2)), type = rep(0:1, P))
  d <- merge(merge(mods, data.frame(question = factor(1:nq))), data.frame(x = 0:1))
  sm_ <- rnorm(P, 0, 0.4)[as.integer(mods$provider)] + rnorm(M, 0, 0.3); sm_ <- sm_ - mean(sm_) + delta
  eta <- 0.5 + 0.6 * d$type + rnorm(M, 0, 0.3)[d$model] + rnorm(nq, 0, 1.2)[d$question] +
         d$x * (sm_[d$model] + rnorm(nq, 0, 0.7)[d$question])
  d$y <- rbinom(nrow(d), size, plogis(eta)); d$n <- size
  raw <- mean(d$y[d$x == 1] / size) - mean(d$y[d$x == 0] / size)
  f <- tryCatch(suppressWarnings(suppressMessages(glmer(cbind(y, n - y) ~ x * model + (1 + x | question), d, family = binomial))),
                error = function(e) NULL)
  if (is.null(f)) return(c(z = NA, raw = raw, sing = NA))
  b <- fixef(f); V <- as.matrix(vcov(f)); L <- setNames(rep(0, length(b)), names(b))
  L["x"] <- 1; L[grep("^x:model", names(b))] <- 1/M
  c(z = sum(L * b) / sqrt(drop(t(L) %*% V %*% L)), raw = raw, sing = isSingular(f))
}
out <- list()
add <- function(v, val, cond) out[[length(out) + 1]] <<- list(variable = v, value = val, conditions = cond)
for (sc in list(list(nq = 25, size = 1, outcome = "flag", deltas = c(0, -0.5, -1)),
                list(nq = 75, size = 2, outcome = "score", deltas = c(0, 0.3, 0.5)))) {
  for (delta in sc$deltas) {
    reps <- if (delta == 0) reps0 else reps1
    r <- do.call(rbind, mclapply(1:reps, one, nq = sc$nq, size = sc$size, delta = delta, mc.cores = 4))
    base <- list(outcome = sc$outcome, questions = sc$nq, models = M, `effect, logit` = delta, replications = reps)
    side <- if (delta < 0 || sc$outcome == "flag") -1 else 1
    for (tst in c("Wald z", "t")) {
      crit <- if (tst == "Wald z") qnorm(1 - 0.05/3) else qt(1 - 0.05/3, sc$nq - 1)
      add(if (delta == 0) "rejection rate under no effect, one-sided" else "power, one-sided",
          mean(side * r[, "z"] > crit, na.rm = TRUE), c(base, list(test = tst, `nominal alpha` = round(0.05/3, 4))))
    }
    add("mean raw difference, claimset minus PDF", mean(r[, "raw"]), base)
    add("share of singular fits", mean(r[, "sing"], na.rm = TRUE), base)
    add("share of failed fits", mean(is.na(r[, "z"])), base)
  }
}
for (x in out) cat(sprintf("%8.4f  %s | %s\n", x$value, x$variable, paste(unlist(x$conditions), collapse = " | ")))
p <- Sys.getenv("CLAIMSET_RESULTS"); if (nzchar(p)) write_json(out, p, auto_unbox = TRUE, digits = NA)
