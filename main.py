"""
数据处理主程序
整合爬虫、PDF处理、OCR和知识库构建
"""
import argparse
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.data_acquisition import WebScraper, PDFProcessor, OCRConverter
from src.knowledge_base import TextChunker, VectorStore
from src.utils.logger import logger
from src.utils.config_loader import config


class DataPipeline:
    """数据处理管道"""
    
    def __init__(self):
        """初始化管道"""
        self.scraper = WebScraper()
        self.pdf_processor = PDFProcessor()
        self.ocr_converter = OCRConverter()
        self.chunker = TextChunker()
        self.vector_store = VectorStore()
        
        logger.info("数据处理管道初始化完成")
    
    def run_web_scraping(self, urls: list = None):
        """运行网页爬取"""
        logger.info("=" * 50)
        logger.info("开始网页爬取...")
        logger.info("=" * 50)
        
        if urls:
            files = self.scraper.scrape_custom_urls(urls)
        else:
            files = self.scraper.scrape_hongloumeng_sites()
        
        logger.info(f"网页爬取完成,共{len(files)}个文件")
        return files
    
    def run_pdf_processing(self, folder: str = None):
        """
        运行PDF处理
        
        Args:
            folder: 指定处理的文件夹(Article/Book等)，如果为None则处理所有默认文件夹
        """
        logger.info("=" * 50)
        logger.info("开始PDF处理...")
        logger.info("=" * 50)
        
        # 如果指定了文件夹，将其转换为列表
        pdf_folders = [folder] if folder else None
        
        results = self.pdf_processor.batch_process_pdfs(pdf_folders=pdf_folders)
        
        logger.info(f"PDF处理完成 - 成功:{results['success']}, 跳过:{results.get('skipped', 0)}, 需OCR:{len(results['needs_ocr'])}")
        
        # 处理需要OCR的PDF
        if results['needs_ocr']:
            logger.info(f"开始OCR处理{len(results['needs_ocr'])}个扫描版PDF...")
            
            for pdf_path in results['needs_ocr']:
                try:
                    self.ocr_converter.pdf_to_markdown(pdf_path)
                    logger.info(f"OCR处理完成: {pdf_path}")
                except Exception as e:
                    logger.error(f"OCR处理失败 ({pdf_path}): {str(e)}")
        
        return results
    
    def build_knowledge_base(self):
        """构建知识库"""
        logger.info("=" * 50)
        logger.info("开始构建知识库...")
        logger.info("=" * 50)
        
        # 收集所有已处理的文件
        raw_folder = Path(config.get('data_acquisition.raw_data_folder'))
        processed_folder = Path(config.get('data_acquisition.processed_data_folder'))
        ocr_folder = Path(config.get('data_acquisition.ocr_output_folder'))
        
        all_files = []
        
        # 网页爬取的文件
        if raw_folder.exists():
            all_files.extend([str(f) for f in raw_folder.glob('*.md')])
        
        # PDF处理的文件
        if processed_folder.exists():
            all_files.extend([str(f) for f in processed_folder.glob('*.md')])
        
        # OCR处理的文件
        if ocr_folder.exists():
            all_files.extend([str(f) for f in ocr_folder.glob('*.md')])
        
        logger.info(f"找到{len(all_files)}个文档文件")
        
        if not all_files:
            logger.warning("没有找到文档文件,请先运行数据采集")
            return
        
        # 清空现有知识库
        logger.info("清空现有知识库...")
        self.vector_store.clear_collection()
        
        # 分块所有文档
        logger.info("开始文本分块...")
        all_chunks = self.chunker.chunk_documents(all_files)
        
        # 添加到向量数据库
        logger.info("添加到向量数据库...")
        count = self.vector_store.add_documents(all_chunks)
        
        logger.info(f"知识库构建完成,共{count}个文档块")
        
        # 显示统计信息
        stats = self.vector_store.get_collection_stats()
        logger.info(f"知识库统计: {stats}")
    
    def run_full_pipeline(self, scrape_web: bool = True, process_pdf: bool = True):
        """运行完整管道"""
        logger.info("=" * 50)
        logger.info("开始完整数据处理管道")
        logger.info("=" * 50)
        
        # 1. 网页爬取
        if scrape_web:
            try:
                self.run_web_scraping()
            except Exception as e:
                logger.error(f"网页爬取失败: {str(e)}")
        
        # 2. PDF处理
        if process_pdf:
            try:
                self.run_pdf_processing()
            except Exception as e:
                logger.error(f"PDF处理失败: {str(e)}")
        
        # 3. 构建知识库
        try:
            self.build_knowledge_base()
        except Exception as e:
            logger.error(f"知识库构建失败: {str(e)}")
        
        logger.info("=" * 50)
        logger.info("完整管道执行完成!")
        logger.info("=" * 50)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='红楼梦知识库数据处理')
    
    parser.add_argument(
        '--mode',
        choices=['scrape', 'pdf', 'build', 'full'],
        default='full',
        help='运行模式: scrape(爬虫), pdf(PDF处理), build(构建知识库), full(全部)'
    )
    
    parser.add_argument(
        '--urls',
        nargs='+',
        help='自定义爬取的URL列表'
    )
    
    parser.add_argument(
        '--folder',
        help='指定PDF处理文件夹(例如 Book 或 Article)'
    )
    
    args = parser.parse_args()
    
    pipeline = DataPipeline()
    
    if args.mode == 'scrape':
        pipeline.run_web_scraping(args.urls)
    elif args.mode == 'pdf':
        pipeline.run_pdf_processing(folder=args.folder)
    elif args.mode == 'build':
        pipeline.build_knowledge_base()
    else:  # full
        pipeline.run_full_pipeline()


if __name__ == "__main__":
    main()
