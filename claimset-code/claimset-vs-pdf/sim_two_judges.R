# Two judges, their points pooled: level and power of the test of the claimset effect averaged over the models,
# with and without an answer-level random intercept. Design as sim_fixed_models.R (2 x P models, 2 conditions;
# flags on 25 questions, score on 75; the effect varies by provider (SD 0.4), model (0.3) and question (0.7)),
# and each answer has a quality of its own (SD sa, the same for both judges), which each judge reads with noise
# of its own (SD 0.5) and a bias (the second judge 0.2 harsher on the logit scale). Each judge gives the score as
# 2 binomial points (or a flag as 1); the two judges' points are pooled: n = 4 (score) or 2 (flag).
# Models: glmer, logit, y ~ condition x model + (1 + condition | question), without and with (1 | answer); the
# tested quantity is the mean of the model effects, by t on (questions - 1) degrees of freedom, one-sided at 0.05/3.
#     Rscript sim_two_judges.R [null reps 500] [power reps 200] [providers 5] [answer SD 1.5]
suppressMessages({library(lme4); library(parallel); library(jsonlite)})
args <- commandArgs(TRUE); reps0 <- if (length(args) > 0) as.integer(args[1]) else 500
reps1 <- if (length(args) > 1) as.integer(args[2]) else 200
P <- if (length(args) > 2) as.integer(args[3]) else 5; M <- 2 * P
sa <- if (length(args) > 3) as.numeric(args[4]) else 1.5

delta_of <- function(f) {
  b <- fixef(f); V <- as.matrix(vcov(f)); L <- setNames(rep(0, length(b)), names(b))
  L["x"] <- 1; L[grep("^x:model", names(b))] <- 1/M
  sum(L * b) / sqrt(drop(t(L) %*% V %*% L))
}
fit <- function(form, d) tryCatch(suppressWarnings(suppressMessages(glmer(form, d, family = binomial))), error = function(e) NULL)

one <- function(s, nq, size, delta) {
  set.seed(s)
  mods <- data.frame(model = factor(1:M), provider = factor(rep(1:P, each = 2)), type = rep(0:1, P))
  d <- merge(merge(mods, data.frame(question = factor(1:nq))), data.frame(x = 0:1))
  d$answer <- factor(seq_len(nrow(d)))
  sm_ <- rnorm(P, 0, 0.4)[as.integer(mods$provider)] + rnorm(M, 0, 0.3); sm_ <- sm_ - mean(sm_) + delta
  eta <- 0.5 + 0.6 * d$type + rnorm(M, 0, 0.3)[d$model] + rnorm(nq, 0, 1.2)[d$question] +
         d$x * (sm_[d$model] + rnorm(nq, 0, 0.7)[d$question]) + rnorm(nrow(d), 0, sa)
  j1 <- rbinom(nrow(d), size, plogis(eta + rnorm(nrow(d), 0, 0.5)))
  j2 <- rbinom(nrow(d), size, plogis(eta - 0.2 + rnorm(nrow(d), 0, 0.5)))
  d$y <- j1 + j2; d$n <- 2 * size
  f0 <- fit(cbind(y, n - y) ~ x * model + (1 + x | question), d)
  f1 <- fit(cbind(y, n - y) ~ x * model + (1 + x | question) + (1 | answer), d)
  c(t0 = if (is.null(f0)) NA else delta_of(f0), t1 = if (is.null(f1)) NA else delta_of(f1),
    sing1 = if (is.null(f1)) NA else isSingular(f1), agree = cor(j1, j2))
}
out <- list()
add <- function(v, val, cond) out[[length(out) + 1]] <<- list(variable = v, value = val, conditions = cond)
for (sc in list(list(nq = 25, size = 1, outcome = "flag", deltas = c(0, -0.5, -1)),
                list(nq = 75, size = 2, outcome = "score", deltas = c(0, 0.3, 0.5)))) {
  for (delta in sc$deltas) {
    reps <- if (delta == 0) reps0 else reps1
    r <- do.call(rbind, mclapply(1:reps, one, nq = sc$nq, size = sc$size, delta = delta, mc.cores = 4))
    base <- list(outcome = sc$outcome, questions = sc$nq, models = M, `effect, logit` = delta, replications = reps,
                 `answer SD` = sa)
    side <- if (delta < 0 || sc$outcome == "flag") -1 else 1
    crit <- qt(1 - 0.05/3, sc$nq - 1)
    for (m in c("t0", "t1")) {
      add(if (delta == 0) "rejection rate under no effect, one-sided" else "power, one-sided",
          mean(side * r[, m] > crit, na.rm = TRUE),
          c(base, list(model = if (m == "t0") "pooled points" else "pooled points + (1 | answer)", `nominal alpha` = round(0.05/3, 4))))
    }
    add("share of failed fits, with (1 | answer)", mean(is.na(r[, "t1"])), base)
    add("share of singular fits, with (1 | answer)", mean(r[, "sing1"], na.rm = TRUE), base)
    add("correlation of the two judges' points", mean(r[, "agree"]), base)
  }
}
for (x in out) cat(sprintf("%8.4f  %s | %s\n", x$value, x$variable, paste(unlist(x$conditions), collapse = " | ")))
p <- Sys.getenv("CLAIMSET_RESULTS"); if (nzchar(p)) write_json(out, p, auto_unbox = TRUE, digits = NA)
