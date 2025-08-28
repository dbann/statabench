# TODO List - Benchmark Runner Enhancements

## 🔍 Quality Assurance
- [ ] **Check that items are being answered fairly by the models**
  - Review current question responses to ensure evaluation correctness
  - Verify models aren't systematically disadvantaged by question format
  - Test edge cases and ambiguous questions
  - Validate scoring logic across different answer types

## 📚 Content Expansion  
- [ ] **Add additional benchmark items to expand test coverage**
  - Create more questions across different Stata domains
  - Add varying difficulty levels (beginner, intermediate, advanced)
  - Include more diverse question formats
  - Ensure balanced representation across topic areas

## 🚀 Frontier Model Integration
- [ ] **Add option to compare with frontier API model**
  - Implement support for OpenAI GPT-4/GPT-3.5
  - Add Anthropic Claude API integration
  - Include other commercial models (Gemini, etc.)
  - Handle API authentication and rate limiting
  - Add cost tracking for API calls

## 📄 Enhanced Reporting
- [ ] **Create nice markdown format output for model comparisons**
  - Generate structured markdown reports
  - Include comparison tables with statistics
  - Add performance rankings and insights
  - Create exportable summary documents
  - Include methodology and limitations sections

## 🔧 Additional Improvements
- [ ] **Add configuration file support**
  - YAML/JSON config for default settings
  - Model-specific parameter presets
  - Custom scoring rules per question type

- [ ] **Implement resume capability**
  - Save progress state during long runs
  - Resume interrupted benchmark sessions
  - Skip already completed questions

- [ ] **Add detailed error reporting**
  - Log API failures and retries
  - Track model-specific error patterns
  - Generate error analysis reports