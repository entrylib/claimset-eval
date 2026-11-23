# Type I error of frequentist small-sample tests of the averaged claimset effect, under no average effect.
# Same design and data-generating process as sim_type1.R (8 models, 4 providers x fast/reasoning;
# effect SD 0.4 by provider, 0.3 by model, 0.7 by question; mean 0).
# Methods: linear mixed model (REML) with Satterthwaite or Kenward-Roger degrees of freedom, on the
# 0/1 flag or the 0-1/2-1 score; logistic mixed model with provider and model slopes, Wald t on 3 df.
suppressMessages({library(lme4); library(lmerTest); library(parallel); library(jsonlite)})
args <- commandArgs(TRUE); reps <- if (length(args)) as.integer(args[1]) else 300

one <- function(s, nq, size, sdq) {
  set.seed(s)
  mods <- data.frame(model = factor(1:8), provider = factor(rep(1:4, each = 2)), type = rep(0:1, 4))
  qs <- data.frame(question = factor(1:nq), paper = factor(rep(1:5, length.out = nq)))
  d <- merge(merge(mods, qs), data.frame(x = 0:1))
  slope_m <- rnorm(4, 0, 0.4)[as.integer(mods$provider)] + rnorm(8, 0, 0.3)
  eta <- 0.5 + 0.6 * d$type + rnorm(8, 0, 0.3)[d$model] + rnorm(nq, 0, 1.2)[d$question] +
         d$x * (slope_m[d$model] + rnorm(nq, 0, sdq)[d$question])
  d$y <- rbinom(nrow(d), size, plogis(eta)); d$n <- size; d$Y <- d$y / size
  L <- function(nm) { v <- setNames(rep(0, length(nm)), nm); v["x"] <- 1; v["x:type"] <- 1/2; v }
  lin <- tryCatch(suppressWarnings(suppressMessages(
    lmerTest::lmer(Y ~ x * type + paper + provider + (1 + x | model) + (1 + x | question), d, REML = TRUE))), error = function(e) NULL)
  res <- c(S_t = NA, S_df = NA, KR_t = NA, KR_df = NA, lin_sing = NA, g_z = NA, g_sing = NA)
  if (!is.null(lin)) {
    l <- L(names(fixef(lin)))
    cs <- contest(lin, matrix(l, 1), ddf = "Satterthwaite", joint = FALSE)
    ck <- contest(lin, matrix(l, 1), ddf = "Kenward-Roger", joint = FALSE)
    res[c("S_t", "S_df", "KR_t", "KR_df", "lin_sing")] <- c(cs$`t value`, cs$df, ck$`t value`, ck$df, isSingular(lin))
  }
  g <- tryCatch(suppressWarnings(suppressMessages(glmer(cbind(y, n - y) ~ x * type + paper + provider +
         (1 + x | provider) + (1 + x | model) + (1 + x | question), d, family = binomial))), error = function(e) NULL)
  if (!is.null(g)) {
    b <- fixef(g); V <- as.matrix(vcov(g)); l <- L(names(b))
    res[c("g_z", "g_sing")] <- c(sum(l * b) / sqrt(drop(t(l) %*% V %*% l)), isSingular(g))
  }
  res
}

out <- list()
add <- function(v, val, cond) out[[length(out) + 1]] <<- list(variable = v, value = val, conditions = cond)
for (sc in list(list(nq = 25, size = 1, sdq = 0.7), list(nq = 75, size = 2, sdq = 0.7))) {
  r <- do.call(rbind, mclapply(1:reps, one, nq = sc$nq, size = sc$size, sdq = sc$sdq, mc.cores = 4))
  base <- list(questions = sc$nq, outcome = if (sc$size == 1) "binary" else "score", `question slope SD` = sc$sdq, replications = reps)
  for (alpha in c(0.01, 0.01/3)) {
    add("rejection rate under no effect, one-sided", mean(r[, "S_t"] > qt(1 - alpha, r[, "S_df"]), na.rm = TRUE),
        c(base, list(model = "linear mixed, REML", test = "Satterthwaite t", `nominal alpha` = round(alpha, 4))))
    add("rejection rate under no effect, one-sided", mean(r[, "KR_t"] > qt(1 - alpha, r[, "KR_df"]), na.rm = TRUE),
        c(base, list(model = "linear mixed, REML", test = "Kenward-Roger t", `nominal alpha` = round(alpha, 4))))
    add("rejection rate under no effect, one-sided", mean(r[, "g_z"] > qt(1 - alpha, 3), na.rm = TRUE),
        c(base, list(model = "logistic mixed, provider and model slopes", test = "Wald t, 3 df", `nominal alpha` = round(alpha, 4))))
  }
  add("median degrees of freedom", median(r[, "S_df"], na.rm = TRUE), c(base, list(model = "linear mixed, REML", test = "Satterthwaite t")))
  add("median degrees of freedom", median(r[, "KR_df"], na.rm = TRUE), c(base, list(model = "linear mixed, REML", test = "Kenward-Roger t")))
  add("share of singular fits", mean(r[, "lin_sing"], na.rm = TRUE), c(base, list(model = "linear mixed, REML")))
  add("share of singular fits", mean(r[, "g_sing"], na.rm = TRUE), c(base, list(model = "logistic mixed, provider and model slopes")))
  add("share of failed fits", mean(is.na(r[, "KR_t"])), c(base, list(model = "linear mixed, REML")))
  add("share of failed fits", mean(is.na(r[, "g_z"])), c(base, list(model = "logistic mixed, provider and model slopes")))
}
for (x in out) cat(sprintf("%-8s %s | %s\n", sprintf("%.4f", x$value), x$variable, paste(unlist(x$conditions), collapse = " | ")))
p <- Sys.getenv("CLAIMSET_RESULTS"); if (nzchar(p)) write_json(out, p, auto_unbox = TRUE, digits = NA)
