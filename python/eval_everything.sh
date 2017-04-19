echo "" > eval.figer.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.label.fine_only eval_output/organized/figer/figer.out.fine_only >> eval.figer.log
echo "" >> eval.figer.log
echo "" >> eval.figer.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.label.fine_only eval_output/organized/ucl/ucl.out.fine_only >> eval.figer.log
echo "" >> eval.figer.log
echo "" >> eval.figer.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.label.fine_only eval_output/organized/outs/figer.out.fine_only >> eval.figer.log
echo "" >> eval.figer.log
echo "" >> eval.figer.log

python dfiner/eval/eval.py eval_output/organized/gold/figer.label.coarse eval_output/organized/figer/figer.out.coarse >> eval.figer.log
echo "" >> eval.figer.log
echo "" >> eval.figer.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.label.coarse eval_output/organized/ucl/ucl.out.coarse >> eval.figer.log
echo "" >> eval.figer.log
echo "" >> eval.figer.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.label.coarse eval_output/organized/outs/figer.out.coarse >> eval.figer.log
echo "" >> eval.figer.log
echo "" >> eval.figer.log

python dfiner/eval/eval.py eval_output/organized/gold/figer.label eval_output/organized/figer/figer.out >> eval.figer.log
echo "" >> eval.figer.log
echo "" >> eval.figer.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.label eval_output/organized/ucl/ucl.out >> eval.figer.log
echo "" >> eval.figer.log
echo "" >> eval.figer.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.label eval_output/organized/outs/figer.out >> eval.figer.log
echo "" >> eval.figer.log
echo "" >> eval.figer.log



echo "" > eval.xiang.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label.fine_only eval_output/organized/figer/figer.out.fine_only >> eval.xiang.log
echo "" >> eval.xiang.log
echo "" >> eval.xiang.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label.fine_only eval_output/organized/ucl/ucl.out.fine_only >> eval.xiang.log
echo "" >> eval.xiang.log
echo "" >> eval.xiang.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label.fine_only eval_output/organized/outs/figer.out.fine_only >> eval.xiang.log
echo "" >> eval.xiang.log
echo "" >> eval.xiang.log

python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label.coarse eval_output/organized/figer/figer.out.coarse >> eval.xiang.log
echo "" >> eval.xiang.log
echo "" >> eval.xiang.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label.coarse eval_output/organized/ucl/ucl.out.coarse >> eval.xiang.log
echo "" >> eval.xiang.log
echo "" >> eval.xiang.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label.coarse eval_output/organized/outs/figer.out.coarse >> eval.xiang.log
echo "" >> eval.xiang.log
echo "" >> eval.xiang.log

python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label eval_output/organized/figer/figer.out >> eval.xiang.log
echo "" >> eval.xiang.log
echo "" >> eval.xiang.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label eval_output/organized/ucl/ucl.out >> eval.xiang.log
echo "" >> eval.xiang.log
echo "" >> eval.xiang.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label eval_output/organized/outs/figer.out >> eval.xiang.log
echo "" >> eval.xiang.log
echo "" >> eval.xiang.log




# echo "" > eval.abelation_xiang.log
# python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label.fine_only eval_output/organized/figer/figer.out.fine_only >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log
# python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label.fine_only eval_output/organized/ucl/ucl.out.fine_only >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log
# python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label.fine_only eval_output/organized/outs/figer.out.fine_only >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log

# python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label.coarse eval_output/organized/figer/figer.out.coarse >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log
# python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label.coarse eval_output/organized/ucl/ucl.out.coarse >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log
# python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label.coarse eval_output/organized/outs/figer.out.coarse >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log

python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label eval_output/organized/abelation/figer_docs-noHyp.out >> eval.abelation_xiang.log
echo "" >> eval.abelation_xiang.log
echo "" >> eval.abelation_xiang.log
python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label eval_output/organized/abelation/figer_docs-noKB.out >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log
# echo "" >> eval.abelation_xiang.log
# python dfiner/eval/eval.py eval_output/organized/gold/figer.xiang.label eval_output/organized/abelation/figer.out >> eval.abelation_xiang.log
echo "" >> eval.abelation_xiang.log
echo "" >> eval.abelation_xiang.log
