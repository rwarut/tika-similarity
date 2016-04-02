import urllib2
import json
from vector_ext import Vector, GeoVector, SweetVector, MeasurementVector
import kmeans_ext

def getJsonData(url):
    data = urllib2.urlopen(url).read()
    return json.loads(data)

def createVectors(json, vectorType):
    vectors = []
    for doc in json['response']['docs']:
        if (vectorType == "geo"):
            v = GeoVector(doc['metadata.filePath'][0], doc)
        elif (vectorType == "sweet"):
            v = SweetVector(doc['metadata.filePath'][0], doc)
        elif (vectorType == "measurement"):
            v = MeasurementVector(doc['metadata.filePath'][0], doc)
        elif (vectorType == "grobid"):
            v = Vector(doc['metadata.filePath'][0], doc)
        
        vectors.append(v)
    return vectors

def writeJson(bestCluster, fileName):
    with open(fileName, "w") as jsonF:
        json_data = {}
        clusters = []
        for key in bestCluster[1]:    #clusters

            cluster_Dict = {}
            children = []
            for point in bestCluster[1][key]:
                node = {}
                node["metadata"] = json.dumps(point.allFeatures)
                node["name"] = point.filename.split('/')[-1]
                node["path"] = point.filename
                children.append(node)
                
            cluster_Dict["children"] = children
            cluster_Dict["name"] = "cluster" + str(key)

            clusters.append(cluster_Dict)

        json_data["children"] = clusters
        json_data["name"] = "clusters"
        
        json.dump(json_data, jsonF)


if __name__ == "__main__":
    metadataUrl = {
    "geo" : "http://localhost:8983/solr/polar/select?q=metadata.Geographic_LATITUDE%3A*&rows=500&wt=json&indent=true",
    "sweet" : "http://localhost:8983/solr/polar/select?q=metadata.sweet_concept%3A*&rows=500&wt=json&indent=true",
    "measurement" : "http://localhost:8983/solr/polar/select?q=metadata.measurement_unit%3A*&rows=500&wt=json&indent=true",
#     "grobid" : "http://localhost:8983/solr/polar/select?q=metadata.TEI.xmlns%3A*&rows=50&wt=json&indent=true"
    }
    
    metadataMeasure = {
    "geo" : 0,
    "sweet" : 3,
    "measurement" : 1,
    "grobid" : 2
    }
    
        
    for key, url in metadataUrl.iteritems():
        print "clustering " + key
        res = getJsonData(url)
        vectors = createVectors(res, key)
    
        cluster = kmeans_ext.K_Means_iter(vectors, metadataMeasure[key])
#         print cluster
    
        writeJson(cluster, "clusters_" + key + ".json")
        for i, points in cluster[1].iteritems():
            print "cluster ", i , " : ", len(points)
#             for p in points:
#                 print p.features["metadata.Geographic_LATITUDE"] , "\t" , p.features["metadata.Geographic_LONGITUDE"]



# print vectors[0].features
# for i in range(0, len(vectors)):
#     print vectors[0].jaccard_dist(vectors[i]), " | ", vectors[0].featureSet, " | " , vectors[i].featureSet
#     print vectors[0].cosine_dist(vectors[i]), " | ",  vectors[i].features
#     print vectors[0].edit_dist(vectors[i])
    
# for v in vectors:
#     v.printFeatures()