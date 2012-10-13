(ns completer.matcher
  (:require [clj-json.core :as json]))

(set! *warn-on-reflection* true)

(defonce data*
  (json/parse-string (slurp "../../shareable_medication.json")
                     true))

(defn match? [^String s r]
  (some (fn [^String x] (.startsWith x s))
        (map (fn [^String x] (.toLowerCase x))
             (filter string? (vals r)))))

(defn match [^String s]
  (let [s (.toLowerCase s)]
    (doall
      (remove nil?
              (map (fn [r] (if (match? s r) r nil)) data*)))))

