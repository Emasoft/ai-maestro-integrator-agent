# Implementation Checklist

## Table of Contents

- 4.1 Complete Implementation Checklist
  - 4.1.1 Setup Phase Checklist
  - 4.1.2 Stage One: Quick Scan Checklist
  - 4.1.3 Stage Two: Deep Dive Checklist
  - 4.1.4 Scoring & Decision Checklist
  - 4.1.5 Follow-up Checklist
- 4.2 Quick Reference Tables
  - 4.2.1 Confidence Score Ranges
  - 4.2.2 Scope Complexity Guide
  - 4.2.3 Dimension Weight Summary

---

## 4.1 Complete Implementation Checklist

Use this checklist to implement the two-stage code review process:

### 4.1.1 Setup Phase Checklist

- [ ] Define scoring rubric for your team
- [ ] Create review templates from output formats
- [ ] Train reviewers on methodology
- [ ] Set up code review tools
- [ ] Establish escalation paths
- [ ] Document team-specific adjustments

### 4.1.2 Stage One: Quick Scan Checklist

- [ ] Create quick scan checklist (team-customized)
- [ ] Assess file structure for anomalies
- [ ] Review diff magnitude for concerns
- [ ] Scan for obvious issues
- [ ] Check for immediate red flags
- [ ] Assign initial confidence score
- [ ] Document findings in output format
- [ ] Decide on Stage Two entry

### 4.1.3 Stage Two: Deep Dive Checklist

- [ ] Analyze Functional Correctness
- [ ] Analyze Architecture & Design
- [ ] Analyze Code Quality
- [ ] Analyze Performance
- [ ] Analyze Security
- [ ] Analyze Testing
- [ ] Analyze Backward Compatibility
- [ ] Analyze Documentation

### 4.1.4 Scoring & Decision Checklist

- [ ] Calculate confidence for each dimension
- [ ] Apply dimension weights appropriately
- [ ] Compute final confidence score
- [ ] Determine decision (Approve/Conditional/Reject)
- [ ] Document decision rationale
- [ ] List specific required changes (if any)
- [ ] Communicate findings to author

### 4.1.5 Follow-up Checklist

- [ ] Track changes requested
- [ ] Monitor for author response (no arbitrary deadline per RULE 13)
- [ ] Re-review after modifications
- [ ] Update confidence score after changes
- [ ] Archive review for knowledge sharing
- [ ] Update process based on learnings

---

## 4.2 Quick Reference Tables

### 4.2.1 Confidence Score Ranges

| Score Range | Decision | Action |
|-------------|----------|--------|
| 80-100% | Approved | Merge immediately |
| 70-79% | Quick Scan only | Proceed to Deep Dive |
| 60-79% | Conditional | Request specific changes |
| Below 60% | Rejected | Major rework needed |

### 4.2.2 Scope Complexity Guide

| Stage | Scope Coverage | Focus |
|-------|----------------|-------|
| Quick Scan | File structure + diff magnitude | Surface issues, red flags |
| Deep Dive | All 8 dimensions | Comprehensive analysis |
| Feedback | All findings documentation | Communication, clarity |
| Complete | Full PR evaluation | All aspects covered |

### 4.2.3 Dimension Weight Summary

| Dimension | Weight | Primary Question |
|-----------|--------|------------------|
| Functional Correctness | 20% | Does it work? |
| Security | 20% | Is it safe? |
| Testing | 15% | Is it verified? |
| Architecture | 15% | Is it sustainable? |
| Backward Compatibility | 15% | Does it break things? |
| Code Quality | 10% | Is it maintainable? |
| Performance | 5% | Is it efficient? |
| Documentation | 5% | Is it explained? |
