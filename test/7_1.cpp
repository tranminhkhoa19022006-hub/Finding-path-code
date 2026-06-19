#include <iostream>
#include <vector>
#include <iomanip> 
using namespace std;

class RealSet; 

class IntSet {
private:
    vector<int> data;
public:
    IntSet(int n = 0) { data.resize(n); }

    ~IntSet() {}

    void input() {
        cout << "Nhap so phan tu: ";
        int n; cin >> n;
        data.resize(n);
        cout << "Nhap cac phan tu (so nguyen): ";
        for (int i = 0; i < n; i++) cin >> data[i];
    }

    void output() const {
        cout << "IntSet = {";
        for (size_t i = 0; i < data.size(); i++) {
            cout << data[i]; 
            if (i < data.size() - 1) cout << ", ";
        }
        cout << "}" << endl;
    }

    int getElement(int i) const {
        if (i >= 0 && i < data.size()) return data[i];
        throw out_of_range("Index out of range");
    }

    void setElement(int i, int value) {
        if (i >= 0 && i < data.size()) data[i] = value;
        else throw out_of_range("Index out of range");
    }

    friend RealSet SetToReal(const IntSet& s);
};

class RealSet {
private:
    vector<double> data;
public:
    RealSet(int n = 0) { data.resize(n); }
    ~RealSet() {}

    void output() const {
        cout << "RealSet = {";
        for (size_t i = 0; i < data.size(); i++) {
            cout << fixed << setprecision(2) << data[i]; // in với 2 số sau dấu phẩy
            if (i < data.size() - 1) cout << ", ";
        }
        cout << "}" << endl;
    }

    double getElement(int i) const {
        if (i >= 0 && i < data.size()) return data[i];
        throw out_of_range("Index out of range");
    }

    void setElement(int i, double value) {
        if (i >= 0 && i < data.size()) data[i] = value;
        else throw out_of_range("Index out of range");
    }

    friend RealSet SetToReal(const IntSet& s);
};

RealSet SetToReal(const IntSet& s) {
    RealSet r(s.data.size());
    for (size_t i = 0; i < s.data.size(); i++) {
        r.data[i] = static_cast<double>(s.data[i]);
    }
    return r;
}

int main() {
    IntSet intset;
    RealSet realset;

    intset.input();
    intset.output();

    realset = SetToReal(intset);
    realset.output();

    return 0;
}
