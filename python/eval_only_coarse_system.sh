


echo "" > eval.xiang_predcoarse_only.log

python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label eval_output/organized/figer/figer.out.coarse >> eval.xiang_predcoarse_only.log
echo "" >> eval.xiang_predcoarse_only.log
echo "" >> eval.xiang_predcoarse_only.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label eval_output/organized/ucl/ucl.out.coarse >> eval.xiang_predcoarse_only.log
echo "" >> eval.xiang_predcoarse_only.log
echo "" >> eval.xiang_predcoarse_only.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label eval_output/organized/outs/figer.out.coarse >> eval.xiang_predcoarse_only.log
echo "" >> eval.xiang_predcoarse_only.log
echo "" >> eval.xiang_predcoarse_only.log

