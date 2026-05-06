from src.pipelines import brent, bdi, freightos, usd, consolidation, kpi_dataset


def run_all():
    print("🚀 Running full pipeline...")

    brent.run()
    bdi.run()
    freightos.run()
    usd.run()
    consolidation.run()
    kpi_dataset.run()   # 👈 ESSENCIAL

    print("✅ All pipelines completed")


if __name__ == "__main__":
    run_all()