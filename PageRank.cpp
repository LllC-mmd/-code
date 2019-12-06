#include <stdio.h>
#include <math.h>
#include <iostream>
#include <list>
#include <vector>
#include <algorithm>
#include <numeric>

using namespace std;

vector<int> sort_indexes(const vector<int> &v) {
    vector<int> idx(v.size());
    iota(idx.begin(), idx.end(), 0);
    sort(idx.begin(), idx.end(), [&v](size_t i1, size_t i2) {return v[i1] > v[i2];});
    return idx;
}

class Graph{
    private:
        int V;
        list<int> *adj;
    public:
        vector<bool> visited;
        // Sscc is a vector which contains the nodes that forms a SCC by itself
        vector<int> Sscc;  
        vector<int> dtime;
        vector<int> ftime;
        vector<float> pgr;
        Graph(int v):V(v), visited(v, false), dtime(v, 0), ftime(v, 0), pgr(v, 0), Sscc(){
            adj = new list<int>[v]; 
        };
        void addEdge(int f, int t);
        void DFSvisit(int v, int &time);
        void DFS();
        void sortedDFS(const vector<int> &t, vector<int> &sc, vector<float> &p);
        void scc();
        void pageRank(float eps);
};

void Graph::addEdge(int f, int t){
    adj[f].push_back(t);
}


void Graph::DFSvisit(int v, int &time){
    time += 1;
    dtime[v] = time;
    visited[v] = true;
    list<int>::iterator i;
    for (i = adj[v].begin(); i != adj[v].end(); i++){
        if (!visited[*i]){
            DFSvisit(*i, time);
        }
    }
    time += 1;
    ftime[v] = time;
}


void Graph::DFS(){
    int time = 0;
    for (int v = 0; v < V; v++){
        if (!visited[v]){
            DFSvisit(v, time);
        } 
    }
}


void Graph::sortedDFS(const vector<int> &t, vector<int> &sc, vector<float> &p){
    int time = 0;
    vector<int> id;
    // sort the finish time of nodes in a descending order
    id = sort_indexes(t);
    for (int v = 0; v < V; v++){
        if (!visited[id[v]]){
            DFSvisit(id[v], time);
            if (ftime[id[v]] - dtime[id[v]] == 1){
                sc.push_back(id[v]);
                p[id[v]] = -1;
            }
        }
    }
}

void Graph::scc(){
    // DFS 
    DFS();
    // construction of GT
    Graph pgT(V);
    list<int>::iterator i;
    for (int v = 0; v < V; v++){
        for (i = adj[v].begin(); i != adj[v].end(); i++){
            pgT.addEdge(*i, v);
        }
    }
    // sorted DFS for GT
    pgT.sortedDFS(ftime, Sscc, pgr);
}


void Graph::pageRank(float eps){
    list<int>::iterator i;
    vector<bool> isSscc(V, false);
    int nSscc = 0;
    for (int s : Sscc){
        isSscc[s] = true;
        nSscc += 1;
    }
    for (int v = 0; v < V; v++){
        if (!isSscc[v]){
            pgr[v] = 1.0/(V-nSscc);
        }
    }
    // initialize the probability matrix
    vector<float> M(V*V, 0);
    for (int v = 0; v < V; v++){
        if (!isSscc[v]){
            int sum = 0;
            for (i = adj[v].begin(); i!= adj[v].end(); i++){
                if (!isSscc[*i]){
                    M[*i*V+v] = 1;
                    sum += 1;
                }
            }
            for (i = adj[v].begin(); i!= adj[v].end(); i++){
                    M[*i*V+v] = M[*i*V+v]/sum;
            }
        }
    }
    // PageRank iteration
    double rmse = 100;
    while (rmse >= eps){
        rmse = 0;
        vector<float> pgrTmp(pgr);
        for (int v = 0; v < V; v++){
            if (!isSscc[v]){
                pgr[v] = 0;
                for (int j = 0; j < V; j++){
                    pgr[v] += pgrTmp[j] * M[v*V+j]; 
                }
            }
        }
        for (int v = 0; v < V; v++){
            rmse += (pgr[v]-pgrTmp[v])*(pgr[v]-pgrTmp[v])/(V-nSscc);
        }
        rmse = sqrt(rmse);
    }
}


int main() {
    // read input
    int nNode;
    int nEdge;
    int from, to;
    int nOutput;
    cin >> nNode >> nEdge;
    Graph pg(nNode);
    for (int i = 0; i < nEdge; i++){
        cin >> from >> to;
        pg.addEdge(from, to);
    }
    cin >> nOutput;
    vector<int> qId(nOutput);
    for (int i = 0; i < nOutput; i++){
        cin >> qId[i];   
    }
    // PageRank
    pg.scc();
    pg.pageRank(1e-8);
    // output
    for (int i: qId){
        if (pg.pgr[i] < 0){
            cout << "None" << endl;
        }
        else{
            printf("%.5f\n", pg.pgr[i]);
        }
    }
    return 0;
}