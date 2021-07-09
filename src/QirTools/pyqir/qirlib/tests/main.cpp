//------------------------------------------------------------------------------
// This code was generated by a tool.
// <auto-generated />
//------------------------------------------------------------------------------

#include <map>
#include <memory>
#include <vector>

#include "QirRuntime.hpp"
#include "QirContext.hpp"
#include "SimFactory.hpp"

using namespace Microsoft::Quantum;
using namespace std;

extern "C" void QuantumApplication__Run(
); // QIR interop function.

int main(int argc, char* argv[])
{
    // Initialize simulator.
    auto sim = CreateFullstateSimulator();
    QirContextScope qirctx(sim.get(), false /*trackAllocatedObjects*/);

    // Execute the entry point operation.
    QuantumApplication__Run();

    return 0;
}
