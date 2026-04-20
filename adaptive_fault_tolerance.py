# Adaptive Redundancy Controller
# Option 1: Hybrid Fault-Tolerant Architecture
# Executable Reference Implementation

import random
import statistics
import time

class FaultModel:
    NORMAL = "normal"
    TRANSIENT = "transient"
    BYZANTINE = "byzantine"
    CRASH = "crash"

class ReplicaNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.health = FaultModel.NORMAL
        self.failed = False

    def inject_fault(self, probability=0.1):
        if random.random() < probability:
            self.health = random.choice([
                FaultModel.TRANSIENT,
                FaultModel.BYZANTINE,
                FaultModel.CRASH,
            ])

    def recover(self):
        self.health = FaultModel.NORMAL
        self.failed = False

    def execute(self, true_value=100.0):
        if self.health == FaultModel.CRASH:
            self.failed = True
            raise RuntimeError("Node crashed")
        if self.health == FaultModel.BYZANTINE:
            return true_value + random.uniform(-100, 100)
        if self.health == FaultModel.TRANSIENT:
            return true_value + random.uniform(-10, 10)
        return true_value + random.uniform(-1, 1)

class RedundancyManager:
    def __init__(self, initial_replicas=3):
        self.replicas = [ReplicaNode(i) for i in range(initial_replicas)]

    def scale_up(self):
        self.replicas.append(ReplicaNode(len(self.replicas)))
        print(f"[REDUNDANCY] Scale UP → replicas = {len(self.replicas)}")

    def scale_down(self):
        if len(self.replicas) > 1:
            removed = self.replicas.pop()
            print(f"[REDUNDANCY] Scale DOWN → removed node {removed.node_id}")

    def execute_all(self):
        outputs = []
        for r in self.replicas:
            try:
                outputs.append(r.execute())
            except RuntimeError:
                pass
        return outputs

class AdaptiveController:
    def __init__(self):
        self.stable_cycles = 0

    def monitor(self, outputs):
        if len(outputs) < 2:
            return float("inf")
        return max(outputs) - min(outputs)

    def analyze(self, deviation):
        return deviation > 10

    def plan(self, fault):
        if fault:
            self.stable_cycles = 0
            return "increase"
        else:
            self.stable_cycles += 1
            if self.stable_cycles > 5:
                return "decrease"
        return "none"

    def execute(self, action, redundancy):
        if action == "increase":
            redundancy.scale_up()
        elif action == "decrease":
            redundancy.scale_down()

def vote(outputs):
    return statistics.median(outputs)


def run_experiment(cycles=30):
    redundancy = RedundancyManager()
    controller = AdaptiveController()

    for t in range(cycles):
        print(f"--- Cycle {t} ---")
        for r in redundancy.replicas:
            r.inject_fault(0.2)
        outputs = redundancy.execute_all()
        if not outputs:
            print("All replicas failed")
            continue
        consensus = vote(outputs)
        deviation = controller.monitor(outputs)
        fault = controller.analyze(deviation)
        action = controller.plan(fault)
        controller.execute(action, redundancy)

        print("Outputs:", [round(o,2) for o in outputs])
        print("Consensus:", round(consensus,2))
        print("Deviation:", round(deviation,2))
        print("Action:", action)
        print("Replicas:", len(redundancy.replicas))
        time.sleep(0.1)

if __name__ == "__main__":
    run_experiment()
