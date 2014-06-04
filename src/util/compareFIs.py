"""
 * Copyright 2012-14 Justin A. Debrabant <debrabant@cs.brown.edu> and Matteo Riondato <matteo@cs.brown.edu>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
"""

import os, sys

def errorExit(msg):
    sys.stderr.write(msg)
    sys.exit(1)

def createLargeResults(fileName, minFreq):
    results = dict([])
    with open(fileName) as FILE:
        prevFreq = 1.0
        for line in FILE:
            tokens = line.split("\t")
            itemset = frozenset(tokens[0].split())
            freq = float(tokens[1])
            if freq > prevFreq:
                errorExit("Large results must be sorted\n")
            if freq >= minFreq:
                results[itemset] = freq
                prevFreq = freq
            else:
                break
    return results

def createSampleResults(fileName, minFreq):
    results1 = dict([])
    results2 = dict([])
    with open(fileName) as FILE:
        prevFreq = 1.0
        for line in FILE:
            tokens = line.split("(")
            itemset = frozenset(tokens[0].split())
            tokens2 = tokens[1].split(",")
            freq = float(tokens2[0])
            lb = float(tokens2[1])
            ub = float(tokens2[2][:-2])
            if freq > prevFreq:
                errorExit("Sample results must be sorted\n")
            if freq >= minFreq:
                results1[itemset] = freq
                results2[itemset] = (freq,lb,ub)
                prevFreq = freq
            else:
                break
    return (results1, results2)
 

def main():
    # Verify arguments
    if len(sys.argv) != 5: 
        errorExit("Usage: {} EPS MINFREQ LARGERES SMALLRES\n".format(os.path.basename(sys.argv[0])))
    largeResFileName = sys.argv[3]
    if not os.path.isfile(largeResFileName):
        errorExit("{} does not exist, or is not a file\n".format(largeResFileName))
    sampleResFileName = sys.argv[4]
    if not os.path.isfile(sampleResFileName):
        errorExit("{} does not exist, or is not a file\n".format(sampleResFileName))
    try:
        epsilon = float(sys.argv[1])
    except ValueError:
        errorExit("{} is not a number\n".format(sys.argv[1]))
    try:
        minFreq = float(sys.argv[2])
    except ValueError:
        errorExit("{} is not a number\n".format(sys.argv[2]))

    extendedLargeRes = createLargeResults(largeResFileName, minFreq - epsilon)

    largeRes = dict([])
    for itemset in extendedLargeRes:
        if extendedLargeRes[itemset] >= minFreq: 
            largeRes[itemset] = extendedLargeRes[itemset]

    acceptableFalsePositivesCandidates = set(extendedLargeRes.keys()) - set(largeRes.keys())

    (sampleRes,sampleRes2) = createSampleResults(sampleResFileName, minFreq - (epsilon / 2) )

    largeResSet = set(largeRes.keys())
    sampleResSet = set(sampleRes.keys())

    intersection = largeResSet & sampleResSet

    falseNegatives = largeResSet - sampleResSet

    falsePositives = sampleResSet - largeResSet

    nonAcceptableFalsePositives = falsePositives - acceptableFalsePositivesCandidates
    for itemset in nonAcceptableFalsePositives:
        print(itemset)
    acceptableFalsePositives = falsePositives & acceptableFalsePositivesCandidates

    jaccard = len(intersection) / len(largeResSet | sampleResSet) 

    maxAbsoluteError = 0.0
    absoluteErrorSum = 0.0
    relativeErrorSum = 0.0
    wrongEps = 0
    wrongConfBounds = 0
    wrongConfBounds2 = 0
    maxCBSize = 0.0;
    avgCBSizeSum = 0.0;
    CBSizes = dict([])
    absErrs = dict([])
    for itemset in intersection | acceptableFalsePositives:
        sampleFreq = sampleRes[itemset]
        largeFreq = extendedLargeRes[itemset]
        absoluteError = abs(sampleFreq - largeFreq)
        absErrs[itemset] = absoluteError
        absoluteErrorSum += absoluteError
        if absoluteError > maxAbsoluteError:
            maxAbsoluteError = absoluteError
        if absoluteError > epsilon:
            wrongEps = wrongEps + 1
        CBSize = sampleRes2[itemset][2] - sampleRes2[itemset][1]
        CBSizes[itemset] = CBSize
        avgCBSizeSum = avgCBSizeSum + CBSize
        if CBSize > maxCBSize:
            maxCBSize = CBSize
        if largeFreq > sampleRes2[itemset][2] or largeFreq < sampleRes2[itemset][1]:
            wrongConfBounds = wrongConfBounds + 1
        if CBSize > 2*epsilon:
            wrongConfBounds2 = wrongConfBounds2 + 1
        relativeErrorSum += absoluteError / largeFreq

    sortedAbsErrs = sorted(absErrs.values())
    sortedCBSizes = sorted(CBSizes.values())

    absErrsMin = sortedAbsErrs[0]
    CBSizesMin = sortedCBSizes[0]

    absErrsMax = sortedAbsErrs[-1]
    CBSizesMax = sortedCBSizes[-1]

    absErrsMedian = sortedAbsErrs[len(sortedAbsErrs) // 2]
    CBSizesMedian = sortedCBSizes[len(sortedCBSizes) // 2]

    absErrsFirstQuartile = sortedAbsErrs[len(sortedAbsErrs) // 4]
    CBSizesFirstQuartile = sortedCBSizes[len(sortedCBSizes) // 4]

    absErrsThirdQuartile = sortedAbsErrs[(3 * len(sortedAbsErrs)) // 4]
    CBSizesThirdQuartile = sortedCBSizes[(3 * len(sortedCBSizes)) // 4]


    avgAbsoluteError = absoluteErrorSum / (len(intersection) + len(acceptableFalsePositives))
    avgRelativeError = relativeErrorSum / (len(intersection) + len(acceptableFalsePositives))

    avgCBSize = avgCBSizeSum / (len(intersection) + len(acceptableFalsePositives))

    print("large={},sample={},e={},minFreq={},largeFIs={}".format(os.path.basename(largeResFileName),
        os.path.basename(sampleResFileName), epsilon, minFreq, len(largeResSet)))
    print("inter={},fn={},fp={},maxfp={},nafp={},jaccard={}".format(len(intersection),
        len(falseNegatives), len(falsePositives),
        len(acceptableFalsePositivesCandidates),
        len(nonAcceptableFalsePositives), jaccard))
    print("we={},maxabserr={},avgabserr={},avgrelerr={},minabserr={},1stquartabserr={},medianabserr={},3rdquartabserr={}".format(wrongEps, maxAbsoluteError, avgAbsoluteError, avgRelativeError,absErrsMin,absErrsFirstQuartile,absErrsMedian,absErrsThirdQuartile))
    print("wcb={},wcb2={},maxcbsize={},avgcbsize={},mincbsize={},1stquartcbsize={},mediancbsize={},3rdquartcbsize={}".format(wrongConfBounds,
        wrongConfBounds2, maxCBSize,
        avgCBSize,CBSizesMin,CBSizesFirstQuartile,CBSizesMedian,CBSizesThirdQuartile));
    sys.stderr.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(os.path.basename(largeResFileName),
        os.path.basename(sampleResFileName), epsilon, minFreq,len(largeResSet),
        len(intersection), len(falseNegatives), len(falsePositives), len(acceptableFalsePositivesCandidates),
        len(nonAcceptableFalsePositives), jaccard, wrongEps, maxAbsoluteError,
        avgAbsoluteError, avgRelativeError,
        absErrsMin,absErrsFirstQuartile,absErrsMedian,absErrsThirdQuartile,
        wrongConfBounds, wrongConfBounds2, maxCBSize, avgCBSize,CBSizesMin,CBSizesFirstQuartile,CBSizesMedian,CBSizesThirdQuartile))

if __name__ == "__main__":
    main()

