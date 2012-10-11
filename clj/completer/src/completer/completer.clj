(ns completer.completer
  (:require [clj-json.core :as json]))

(set! *warn-on-reflection* true)

;-------------------------------------------------------------------------------

(defn freeze [data ^String file]
  (with-open [os (-> file
                   (java.io.FileOutputStream.)
                   (java.util.zip.GZIPOutputStream.)
                   (java.io.ObjectOutputStream.))]
    (.writeObject os data)))

(defn thaw [^String file]
  (with-open [is (-> file
                   (java.io.FileInputStream.)
                   (java.util.zip.GZIPInputStream.)
                   (java.io.ObjectInputStream.))]
    (.readObject is)))

;-------------------------------------------------------------------------------

(defn str-prefixes [^String s]
  (for [i (range 1 (inc (.length s)))]
    (.substring s 0 i)))

(defn tokens [r]
  (flatten
    (map (fn [^String x] (into [] (.split x "[^a-z0-9]")))
         (map (fn [^String x] (.toLowerCase x))
              (filter string?
                      (vals r))))))

(defn prefixes [r]
  (into #{}
        (for [t (tokens r)
              p (str-prefixes t)]
          p)))

(defn prefix-index [data]
  (apply (partial merge-with clojure.set/union)
    (for [r data
          p (prefixes r)]
      {p #{(:id r)}})))

;-------------------------------------------------------------------------------

(defonce data*
  (json/parse-string (slurp "../../shareable_medication.json") true))

(defonce by-id*
  (into {}
        (for [r data*]
          {(:id r) r})))

(defonce by-prefix*
  (let [f "./by-prefix.obj.gz"]
    (if (.exists (clojure.java.io/file f))
      (thaw f)
      (do
        (let [bp (prefix-index data*)]
          (freeze bp f)
          bp)))))

(defn by-prefix [p]
  (doall
    (map by-id* (by-prefix* p))))

