/**
 * Calculation engine for Taiwan parenting subsidies.
 * Must produce identical results to Python apps/calculator/engine.py.
 */

const SubsidyEngine = (() => {
  "use strict";

  function findAmount(amounts, birthOrder) {
    let result = 0;
    for (const entry of amounts || []) {
      if (entry.birth_order === birthOrder) {
        return entry.monthly || entry.amount || 0;
      }
      if (entry.birth_order === 3 && birthOrder >= 3) {
        result = entry.monthly || entry.amount || 0;
      }
    }
    return result;
  }

  function calculateBirthBonus(cityData, birthOrder) {
    if (!cityData || !cityData.amounts) return null;

    const amount = findAmount(cityData.amounts, birthOrder);
    if (amount > 0) {
      return {
        name: "生育獎勵金",
        type: "one_time",
        amount: amount,
        notes: ["第" + birthOrder + "胎"],
      };
    }
    return null;
  }

  function calculateChildcareAllowance(
    centralData,
    citySupplement,
    birthOrder,
    incomeTaxRate
  ) {
    const limit = (centralData.eligibility || {}).income_tax_rate_limit || 20;
    if (incomeTaxRate >= limit) return null;

    const centralAmount = findAmount(centralData.base_amounts, birthOrder);

    let supplement = 0;
    if (citySupplement && citySupplement.amounts) {
      supplement = findAmount(citySupplement.amounts, birthOrder);
    }

    const total = centralAmount + supplement;
    if (total > 0) {
      const notes = ["中央 " + centralAmount.toLocaleString() + " 元/月"];
      if (supplement > 0) {
        notes.push("地方加碼 " + supplement.toLocaleString() + " 元/月");
      }
      return {
        name: "育兒津貼",
        type: "monthly",
        amount: total,
        duration_months: 60,
        notes: notes,
      };
    }
    return null;
  }

  function calculateDaycareSubsidy(
    centralData,
    citySupplement,
    birthOrder,
    careType,
    incomeTaxRate
  ) {
    if (careType !== "public" && careType !== "quasi_public") return null;

    const limit = (centralData.eligibility || {}).income_tax_rate_limit || 20;
    if (incomeTaxRate >= limit) return null;

    const typeData = centralData[careType] || {};
    let centralAmount = 0;
    for (const entry of typeData.amounts || []) {
      if (entry.birth_order === birthOrder) {
        centralAmount = entry.monthly;
        break;
      }
      if (entry.birth_order === 3 && birthOrder >= 3) {
        centralAmount = entry.monthly;
      }
    }

    const supplementKey = careType + "_supplement";
    let supplement = 0;
    if (citySupplement && citySupplement[supplementKey]) {
      for (const entry of citySupplement[supplementKey]) {
        if (entry.birth_order === birthOrder) {
          supplement = entry.monthly;
          break;
        }
        if (entry.birth_order === 3 && birthOrder >= 3) {
          supplement = entry.monthly;
        }
      }
    }

    const total = centralAmount + supplement;
    if (total > 0) {
      const careLabel =
        careType === "public" ? "公共化托育" : "準公共化托育";
      const notes = [careLabel, "中央 " + centralAmount.toLocaleString() + " 元/月"];
      if (supplement > 0) {
        notes.push("地方加碼 " + supplement.toLocaleString() + " 元/月");
      }
      return {
        name: "托育補助",
        type: "monthly",
        amount: total,
        duration_months: 24,
        notes: notes,
      };
    }
    return null;
  }

  function calculateParentalLeave(parentalLeaveData, insuredSalary) {
    const pl = parentalLeaveData.parental_leave || {};
    const rate = pl.salary_replacement_rate || 0.8;
    const maxMonths = pl.max_months || 6;
    const maxSalary = (pl.calculation || {}).max_insured_salary || 45800;

    const effectiveSalary = Math.min(insuredSalary, maxSalary);
    const amount = Math.floor(effectiveSalary * rate);

    if (amount > 0) {
      return {
        name: "育嬰留停津貼",
        type: "monthly",
        amount: amount,
        duration_months: maxMonths,
        notes: [
          "月投保薪資 " +
            effectiveSalary.toLocaleString() +
            " × " +
            Math.floor(rate * 100) +
            "%",
          "最長 " + maxMonths + " 個月",
        ],
      };
    }
    return null;
  }

  function calculateCentralBirthSubsidy(centralData, insuredSalary) {
    var cbs = centralData.central_birth_subsidy || {};
    var guaranteed = cbs.amount || 100000;

    // Labor insurance birth benefit = avg insured salary × 2 months
    var insuranceBenefit = insuredSalary * 2;
    var topUp = Math.max(0, guaranteed - insuranceBenefit);
    var total = Math.max(guaranteed, insuranceBenefit);

    var notes = [];
    if (insuranceBenefit > 0) {
      notes.push("勞保生育給付 " + insuranceBenefit.toLocaleString() + " 元");
      if (topUp > 0) {
        notes.push("中央補足 " + topUp.toLocaleString() + " 元");
      } else {
        notes.push("勞保給付已超過 10 萬，領取較高金額");
      }
    } else {
      notes.push("無社會保險，中央全額補助 10 萬元");
    }

    return {
      name: "中央生育補助",
      type: "one_time",
      amount: total,
      notes: notes,
    };
  }

  function estimateMonthlyCost(careType, feeData, cityPublicFee) {
    const feeRanges = feeData.fee_ranges || {};

    const typeMap = {
      self: 0,
      public: "public_daycare",
      quasi_public: "quasi_public_center",
      private: "private_center",
    };

    const feeKey = typeMap[careType] || 0;
    if (feeKey === 0) return 0;

    if (
      careType === "public" &&
      cityPublicFee &&
      cityPublicFee.monthly_fee
    ) {
      return cityPublicFee.monthly_fee;
    }

    const rangeData = feeRanges[feeKey] || {};
    return rangeData.typical || 0;
  }

  function calculateRecommendedMonths(careType) {
    const months = [];

    for (let month = 1; month <= 12; month++) {
      let score = 50;
      const pros = [];
      const cons = [];

      if (careType === "public" || careType === "quasi_public") {
        if ([11, 12, 1].includes(month)) {
          score += 30;
          pros.push("出生後 3-5 個月趕上隔年四月公托招生");
        } else if ([2, 3].includes(month)) {
          score += 10;
          pros.push("可能趕上同年七月第二梯次招生");
        } else if ([4, 5].includes(month)) {
          score -= 10;
          cons.push("剛出生無法立即入托，需等下次招生梯次");
        } else if ([6, 7, 8].includes(month)) {
          score -= 5;
          cons.push("需等隔年四月招生，等待期較長");
        }

        if ([10, 11, 12].includes(month)) {
          score += 10;
          pros.push("六個月育嬰假結束時間接近公托招生期");
        }
      } else {
        pros.push("私托或自行照顧，入托時間較彈性");
      }

      if ([1, 2].includes(month)) {
        pros.push("農曆年後有較多行政資源處理申請");
      }
      if ([9, 10].includes(month)) {
        score += 5;
        pros.push("可趕上下年度政府預算的補助調整");
      }

      months.push({
        month: month,
        score: Math.min(100, Math.max(0, score)),
        pros: pros,
        cons: cons,
        recommended: score >= 70,
      });
    }

    return months;
  }

  function calculateAll(userInput, subsidyData) {
    const output = {
      one_time_subsidies: [],
      monthly_subsidies: [],
      monthly_cost_estimate: 0,
      monthly_subsidy_total: 0,
      monthly_net_cost: 0,
      recommended_birth_months: [],
      notes: [],
    };

    const centralBirthData = subsidyData.central_birth_subsidy || {};
    const birthBonusData = subsidyData.birth_bonus || {};
    const childcareData = subsidyData.childcare_allowance || {};
    const daycareData = subsidyData.daycare_subsidy || {};
    const parentalLeaveData = subsidyData.parental_leave || {};
    const feeData = subsidyData.daycare_fees || {};

    const cityCode = userInput.city_code;

    // 0. Central birth subsidy (2026 guaranteed 100k)
    const cbs = calculateCentralBirthSubsidy(
      centralBirthData,
      userInput.insured_salary
    );
    if (cbs) output.one_time_subsidies.push(cbs);

    // 1. Birth bonus
    const cityBonus = (birthBonusData.cities || {})[cityCode] || {};
    const bonus = calculateBirthBonus(cityBonus, userInput.birth_order);
    if (bonus) output.one_time_subsidies.push(bonus);

    // 2. Childcare allowance (only if self-care or private)
    if (
      userInput.care_type === "self" ||
      userInput.care_type === "private"
    ) {
      const ca = calculateChildcareAllowance(
        childcareData.central || {},
        (childcareData.city_supplements || {})[cityCode] || {},
        userInput.birth_order,
        userInput.income_tax_rate
      );
      if (ca) output.monthly_subsidies.push(ca);
    }

    // 3. Daycare subsidy (only if public or quasi_public)
    if (
      userInput.care_type === "public" ||
      userInput.care_type === "quasi_public"
    ) {
      const ds = calculateDaycareSubsidy(
        daycareData.central || {},
        (daycareData.city_supplements || {})[cityCode] || {},
        userInput.birth_order,
        userInput.care_type,
        userInput.income_tax_rate
      );
      if (ds) output.monthly_subsidies.push(ds);
    }

    // 4. Parental leave
    if (userInput.parental_leave && userInput.insured_salary > 0) {
      const pl = calculateParentalLeave(
        parentalLeaveData,
        userInput.insured_salary
      );
      if (pl) output.monthly_subsidies.push(pl);
    }

    // 5. Cost estimate
    const cityPublicFee =
      (feeData.city_public_fees || {})[cityCode] || {};
    output.monthly_cost_estimate = estimateMonthlyCost(
      userInput.care_type,
      feeData,
      cityPublicFee
    );

    // Calculate totals
    output.monthly_subsidy_total = output.monthly_subsidies
      .filter((s) => s.name !== "育嬰留停津貼")
      .reduce((sum, s) => sum + s.amount, 0);
    output.monthly_net_cost = Math.max(
      0,
      output.monthly_cost_estimate - output.monthly_subsidy_total
    );

    // 6. Recommended birth months
    output.recommended_birth_months = calculateRecommendedMonths(
      userInput.care_type
    );

    return output;
  }

  return {
    calculateAll: calculateAll,
    calculateCentralBirthSubsidy: calculateCentralBirthSubsidy,
    calculateBirthBonus: calculateBirthBonus,
    calculateChildcareAllowance: calculateChildcareAllowance,
    calculateDaycareSubsidy: calculateDaycareSubsidy,
    calculateParentalLeave: calculateParentalLeave,
    estimateMonthlyCost: estimateMonthlyCost,
    calculateRecommendedMonths: calculateRecommendedMonths,
  };
})();
